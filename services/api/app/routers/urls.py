from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.models.requests import CreateShortUrlRequest
from app.models.responses import CreateShortUrlResponse
from app.services.url_service import create_short_url, get_url_by_code
from app.utils.logger import logger

router = APIRouter()

@router.get("/health")
def health():
    """Health check endpoint."""
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

@router.get("/{short_code}")
async def redirect_url(short_code: str):
    try:
        url_data = await get_url_by_code(short_code)

        if not url_data:
            raise HTTPException(status_code=404, detail="Short URL not found")

        return RedirectResponse(url=url_data.originalUrl, status_code=307)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")