import httpx
from typing import Optional, Dict, Any
from fastapi import Request
from app.models.database import analyticsEvent
from app.utils.dynamodb_client import ANALYTICS_TABLE, URLS_TABLE, put_item, increment_counter
from app.utils.hashing import hash_ip
from app.utils.user_agent_parser import parse_user_agent
from app.utils.time_utils import get_current_timestamp, add_days
from app.utils.logger import logger

async def get_geolocation(ip: str) -> Dict[str, str]:
    if ip.startswith(('127.', '10.', '172.', '192.168.', '::1', 'localhost')):
        return {
            "country": "Unknown",
            "region": "Unknown",
            "city": "Unknown"
        }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"https://ip-api.com/json/{ip}")

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "country": data.get("country", "Unknown"),
                        "region": data.get("regionName", "Unknown"),
                        "city": data.get("city", "Unknown")
                    }
    except Exception as e:
        logger.error(f"Error getting geolocation for {ip}: {e}")

    return {
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown"
    }

async def track_click(short_code: str, request: Request) -> bool:
    try:
        ip = request.client.host if request.client else "unknown"

        geo = await get_geolocation(ip)

        user_agent = request.headers.get("user-agent", "")
        device_info = parse_user_agent(user_agent)

        referrer = request.headers.get("referer", "direct")

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

        success = put_item(ANALYTICS_TABLE, event.model_dump())

        if success:
            logger.info(f"Tracked click for {short_code}")

        return success

    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return False

async def increment_click_counter(short_code: str) -> bool:
    try:
        result = increment_counter(
            URLS_TABLE,
            {'shortCode': short_code},
            'clickCount'
        )
        return result is not None
    except Exception as e:
        logger.error(f"Error incrementing click counter: {e}")
        return False