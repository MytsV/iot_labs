from dataclasses import dataclass

from datetime import datetime
from domain.gyroscope import Gyroscope
from domain.gps import Gps


@dataclass
class AggregatedData:
    gyroscope: Gyroscope
    gps: Gps
    timestamp: datetime
    user_id: int
