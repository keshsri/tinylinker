from typing import Optional
import os
from app.models.database import ShortUrl
from app.models.requests import CreateShortUrlRequest
from app.models.responses import CreateShortUrlResponse
from app.utils.dynamodb_client import URLS_TABLE, put_item, get_item
from app.utils.code_generator import generate_short_code, is_valid_short_code
from app.utils.time_utils import get_current_timestamp, add_seconds
from app.utils.logger import logger

BASE_URL = os.environ.get('BASE_URL', 'https://tinylinker.ly')

async def create_short_url(request: CreateShortUrlRequest, user_id: str = "anonymous") -> CreateShortUrlResponse:
    logger.info(f"Creating short URL for: {request.url}")
    
    if request.customAlias:
        logger.info(f"Custom alias requested: {request.customAlias}")
        if not is_valid_short_code(request.customAlias):
            logger.warning(f"Invalid custom alias format: {request.customAlias}")
            raise ValueError("Invalid custom alias format")

        existing = get_item(URLS_TABLE, {'shortCode': request.customAlias})
        if existing:
            logger.warning(f"Custom alias already taken: {request.customAlias}")
            raise ValueError(f"Custom alias '{request.customAlias}' is already taken")

        short_code = request.customAlias
        is_custom = True
    else:
        logger.info("Generating random short code")
        short_code = await generate_unique_short_code()
        is_custom = False

    created_at = get_current_timestamp()
    expires_at = add_seconds(created_at, request.expiresIn) if request.expiresIn else None

    url_item = ShortUrl(
        shortCode=short_code,
        originalUrl=str(request.url),
        userId=user_id,
        createdAt=created_at,
        expiresAt=expires_at,
        clickCount=0,
        customAlias=is_custom,
        isSafe=True
    )

    logger.info(f"Saving short URL to DynamoDB: {short_code}")
    success = put_item(URLS_TABLE, url_item.model_dump())
    if not success:
        logger.error(f"Failed to save short URL: {short_code}")
        raise Exception("Failed to create short URL")

    logger.info(f"Short URL created successfully: {short_code}")
    return CreateShortUrlResponse(
        shortCode=short_code,
        shortUrl=f"{BASE_URL}/{short_code}",
        originalUrl=str(request.url),
        createdAt=created_at,
        expiresAt=expires_at,
        isSafe=True
    )

async def generate_unique_short_code(max_attempts: int = 3) -> str:
    logger.info(f"Generating unique short code (max attempts: {max_attempts})")
    for attempt in range(max_attempts):
        code = generate_short_code()
        logger.info(f"Attempt {attempt + 1}: Generated code {code}")
        existing = get_item(URLS_TABLE, {'shortCode': code})
        if not existing:
            logger.info(f"Unique code found: {code}")
            return code
        logger.warning(f"Code collision detected: {code}")

    logger.warning(f"Max attempts reached, generating 8-character code")
    return generate_short_code(length=8)

async def get_url_by_code(short_code: str) -> Optional[ShortUrl]:
    logger.info(f"Fetching URL data for short code: {short_code}")
    item = get_item(URLS_TABLE, {'shortCode': short_code})
    if not item:
        logger.warning(f"Short code not found in database: {short_code}")
        return None

    logger.info(f"URL data retrieved for: {short_code}")
    return ShortUrl(**item)