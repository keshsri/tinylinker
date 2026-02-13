from pydantic import BaseModel
from typing import Optional, List, Dict

class CreateShortUrlResponse(BaseModel):
    shortCode: str
    shortUrl: str
    originalUrl: str
    createdAt: int
    expiresAt: Optional[int] = None
    isSafe: bool = True

class TimeSeriesData(BaseModel):
    timestamp: str
    clicks: int

class CountryData(BaseModel):
    country: str
    clicks: int

class DeviceData(BaseModel):
    device: str
    clicks: int

class ReferrerData(BaseModel):
    referrer: str
    clicks: int

class AnalyticsResponse(BaseModel):
    shortCode: str
    totalClicks: int
    uniqueIPs: int
    timeRange: Dict[str, int]
    clicksByTime: Optional[List[TimeSeriesData]] = None
    clicksByCountry: Optional[List[CountryData]] = None
    clicksByDevice: Optional[List[DeviceData]] = None
    topReferrers: Optional[List[ReferrerData]] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict] = None