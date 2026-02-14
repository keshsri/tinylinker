import httpx
from typing import Optional, Dict, Any, List
from fastapi import Request
from collections import Counter
from app.models.database import analyticsEvent
from app.utils.dynamodb_client import ANALYTICS_TABLE, URLS_TABLE, put_item, increment_counter, query_items
from app.utils.hashing import hash_ip
from app.utils.user_agent_parser import parse_user_agent
from app.utils.time_utils import get_current_timestamp, add_days
from app.utils.logger import logger
from boto3.dynamodb.conditions import Key

async def get_geolocation(ip: str) -> Dict[str, str]:
    logger.info(f"Getting geolocation for IP: {ip}")
    if ip.startswith(('127.', '10.', '172.', '192.168.', '::1', 'localhost')):
        logger.info(f"Private/local IP detected: {ip}")
        return {
            "country": "Unknown",
            "region": "Unknown",
            "city": "Unknown"
        }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"http://ip-api.com/json/{ip}")
            logger.info(f"IP geolocation API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"API response data: {data}")
                if data.get("status") == "success":
                    logger.info(f"Geolocation retrieved successfully for: {ip}")
                    return {
                        "country": data.get("country", "Unknown"),
                        "region": data.get("regionName", "Unknown"),
                        "city": data.get("city", "Unknown")
                    }
                else:
                    logger.warning(f"API returned non-success status: {data.get('status')} - {data.get('message', 'No message')}")
    except Exception as e:
        logger.error(f"Error getting geolocation for {ip}: {e}")

    logger.warning(f"Returning unknown geolocation for: {ip}")
    return {
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown"
    }

async def track_click(short_code: str, request: Request) -> bool:
    logger.info(f"Tracking click for short code: {short_code}")
    try:
        ip = request.client.host if request.client else "unknown"
        logger.info(f"Client IP: {ip}")

        geo = await get_geolocation(ip)

        user_agent = request.headers.get("user-agent", "")
        device_info = parse_user_agent(user_agent)
        logger.info(f"Device info: {device_info['device']}, Browser: {device_info['browser']}")

        referrer = request.headers.get("referer", "direct")
        logger.info(f"Referrer: {referrer}")

        timestamp = get_current_timestamp()

        event = analyticsEvent(
            shortCode=short_code,
            timestamp=timestamp,
            ipHash=hash_ip(ip),
            country=geo["country"],
            region=geo["region"],
            city=geo["city"],
            device=device_info["device"],
            browser=device_info["browser"],
            os=device_info["os"],
            referrer=referrer,
            expiresAt=add_days(timestamp, 15)
        )

        logger.info(f"Saving analytics event to DynamoDB for: {short_code}")
        success = put_item(ANALYTICS_TABLE, event.model_dump())

        if success:
            logger.info(f"Click tracked successfully for: {short_code}")
        else:
            logger.error(f"Failed to save analytics event for: {short_code}")

        return success

    except Exception as e:
        logger.error(f"Error tracking click for {short_code}: {e}")
        return False

async def increment_click_counter(short_code: str) -> bool:
    logger.info(f"Incrementing click counter for: {short_code}")
    try:
        result = increment_counter(
            URLS_TABLE,
            {'shortCode': short_code},
            'clickCount'
        )
        if result is not None:
            logger.info(f"Click counter incremented to {result} for: {short_code}")
            return True
        else:
            logger.error(f"Failed to increment click counter for: {short_code}")
            return False
    except Exception as e:
        logger.error(f"Error incrementing click counter for {short_code}: {e}")
        return False

async def get_analytics(short_code: str) -> Dict[str, Any]:
    logger.info(f"Fetching analytics for short code: {short_code}")
    try:
        items = query_items(
            ANALYTICS_TABLE,
            'shortCode = :code',
            {':code': short_code}
        )

        if not items:
            logger.info(f"No analytics data found for: {short_code}")
            return {
                "shortCode": short_code,
                'totalClicks': 0,
                'clicksByCountry': {},
                "clicksByDevice": {},
                "clicksByBrowser": {},
                "clicksByReferrer": {},
                "recentClicks": []
            }

        logger.info(f"Processing {len(items)} analytics events for: {short_code}")
        countries = Counter(item['country'] for item in items)
        devices = Counter(item['device'] for item in items)
        browsers = Counter(item['browser'] for item in items)
        referrers = Counter(item['referrer'] for item in items)

        recent = sorted(items, key=lambda x: x['timestamp'], reverse=True)[:10]
        recent_clicks = [
            {
                "timestamp": item['timestamp'],
                "country": item['country'],
                "city": item['city'],
                "device": item['device'],
                "browser": item['browser'],
                "os": item['os'],
                'referrer': item['referrer']
            }
            for item in recent
        ]

        logger.info(f"Analytics aggregated successfully for: {short_code}")
        return {
            "shortCode": short_code,
            "totalClicks": len(items),
            "clicksByCountry": dict(countries),
            "clicksByDevice": dict(devices),
            "clicksByBrowser": dict(browsers),
            "clicksByReferrer": dict(referrers),
            "recentClicks": recent_clicks
        }
    except Exception as e:
        logger.error(f"Error getting analytics for {short_code}: {e}")
        return {
            "shortCode": short_code,
            "totalClicks": 0,
            "error": str(e)
        }