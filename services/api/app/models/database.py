from pydantic import BaseModel
from typing import Optional, Dict

class ShortUrl(BaseModel):
    shortCode: str
    originalUrl: str
    userId: str
    createdAt: int
    expiresAt: Optional[int] = None
    clickCount: int = 0
    customAlias: bool = False
    isSafe: bool = True
    preview: Optional[Dict[str, str]] = None
    lastClickedAt: Optional[int] = None

class analyticsEvent(BaseModel):
    shortCode: str
    timestamp: int
    ipHash: str
    country: str
    region: str
    city: str
    device: str
    browser: str
    os: str
    referrer: str
    expiresAt: int

class RateLimit(BaseModel):
    identifier: str
    windowStart: int
    requestCount: int = 0
    expiresAt: int