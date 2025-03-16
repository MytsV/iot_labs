from datetime import datetime
from pydantic import BaseModel, field_validator


class GyroscopeData(BaseModel):
    x: float
    y: float
    z: float


class AgentData(BaseModel):
    user_id: int
    gyroscope: GyroscopeData
    # gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value):
        # Convert the timestamp to a datetime object
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )
