from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional

class CreateShortUrlRequest(BaseModel):
    url: HttpUrl
    customAlias: Optional[str] = Field(None, min_length=3, max_length=20)
    expiresIn: Optional[int] = Field(None, gt=0, description="TTL in seconds")
    enableWebhook: Optional[bool] = False

    @field_validator('customAlias')
    @classmethod
    def validate_custom_alias(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Custom alias must contain only alphanumeric characters, dashes and underscores')
        return value

class AnalyticsQueryParams(BaseModel):
    timeRange: Optional[str] = Field(None, description="eg., 7d, 30d, 1h")
    groupBy: Optional[str] = Field(None, pattern="^(hour|day|week|month|country|device|browser)$")