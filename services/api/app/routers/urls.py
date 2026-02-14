from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.models.requests import CreateShortUrlRequest
from app.models.responses import CreateShortUrlResponse
from app.services.url_service import create_short_url, get_url_by_code
from app.services.analytics_service import track_click, increment_click_counter, get_analytics
from app.utils.logger import logger

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}

@router.post("/shorten", response_model=CreateShortUrlResponse, status_code=201)
async def shorten_url(request:CreateShortUrlRequest):
    try:
        result = await create_short_url(request)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating short URL: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/preview/{short_code}")
async def preview_url(short_code: str):
    try:
        logger.info(f"Preview request for short code: {short_code}")
        url_data = await get_url_by_code(short_code)

        if not url_data:
            logger.warning(f"Short code not found: {short_code}")
            raise HTTPException(status_code=404, detail="Short URL not found")

        logger.info(f"Preview successful for: {short_code}")
        return {
            "shortCode": short_code,
            "originalUrl": url_data.originalUrl,
            "clickCount": url_data.clickCount,
            "createdAt": url_data.createdAt,
            "expiresAt": url_data.expiresAt,
            "customAlias": url_data.customAlias,
            "isSafe": url_data.isSafe
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting URL preview for {short_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/analytics/{short_code}")
async def get_url_analytics(short_code: str):
    try:
        logger.info(f"Analytics request for short code: {short_code}")
        analytics = await get_analytics(short_code)

        if "error" in analytics:
            logger.error(f"Analytics error for {short_code}: {analytics['error']}")
            raise HTTPException(status_code=500, detail=analytics['error'])

        logger.info(f"Analytics retrieved for {short_code}: {analytics['totalClicks']} clicks")
        return analytics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics for {short_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{short_code}", include_in_schema=False)
async def redirect_url(short_code: str, request: Request):
    try:
        logger.info(f"Redirect request for short code: {short_code}")
        url_data = await get_url_by_code(short_code)

        if not url_data:
            logger.warning(f"Short code not found for redirect: {short_code}")
            raise HTTPException(status_code=404, detail="Short URL not found")

        logger.info(f"Tracking click for: {short_code}")
        await track_click(short_code, request)

        logger.info(f"Incrementing counter for: {short_code}")
        await increment_click_counter(short_code)

        logger.info(f"Redirecting {short_code} to: {url_data.originalUrl}")
        return RedirectResponse(url=url_data.originalUrl, status_code=307)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting {short_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")