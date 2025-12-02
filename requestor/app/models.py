"""Pydantic models for notification requests."""
from pydantic import BaseModel, Field, validator, root_validator, EmailStr
from typing import Optional, List, Any

class IntervalModel(BaseModel):
    """Model for notification scheduling intervals."""
    Once: Optional[bool] = False
    Days: Optional[List[int]] = []
    Weeks: Optional[List[int]] = []
    Months: Optional[List[int]] = []
    Years: Optional[List[int]] = []

    @validator("Days", each_item=True)
    def validate_day(cls, v: int) -> int:
        """Validate day values."""
        if not 1 <= v <= 31:
            raise ValueError("Days must be between 1 and 31")
        return v

    @validator("Weeks", each_item=True)
    def validate_week(cls, v: int) -> int:
        """Validate week values."""
        if not 1 <= v <= 52:
            raise ValueError("Weeks must be between 1 and 52")
        return v

    @validator("Months", each_item=True)
    def validate_month(cls, v: int) -> int:
        """Validate month values."""
        if not 1 <= v <= 12:
            raise ValueError("Months must be between 1 and 12")
        return v

    @validator("Years", each_item=True)
    def validate_year(cls, v: int) -> int:
        """Validate year values."""
        if v < 1970 or v > 2100:
            raise ValueError("Years must be between 1970 and 2100")
        return v

class NotificationRequest(BaseModel):
    """Model for notification requests."""
    Application: str
    Recipient: str
    Subject: Optional[str]
    Message: str
    OutputType: str  # SMS, EMAIL, PUSH
    Date: Optional[str] = None
    Time: Optional[str] = None
    Interval: IntervalModel

    PhoneNumber: Optional[str] = None
    EmailAddresses: Optional[List[EmailStr]] = None
    PushToken: Optional[str] = None

    @root_validator(skip_on_failure=True)
    def validate_delivery_target(cls, values: dict) -> dict:
        """Validate that required delivery targets are provided based on output type."""
        output_type = values.get("OutputType")
        phone = values.get("PhoneNumber")
        emails = values.get("EmailAddresses")
        token = values.get("PushToken")

        if output_type == "SMS" and not phone:
            raise ValueError("PhoneNumber is required for SMS notifications")
        if output_type == "EMAIL" and not emails:
            raise ValueError("EmailAddresses is required for EMAIL notifications")
        if output_type == "PUSH" and not token:
            raise ValueError("PushToken is required for PUSH notifications")

        return values

