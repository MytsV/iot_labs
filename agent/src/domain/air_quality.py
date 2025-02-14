from dataclasses import dataclass
from datetime import datetime

from domain.gps import Gps


@dataclass
class AirQuality:
    pm25: float  # Дрібні тверді частинки (PM2.5) у мкг/м³
    pm10: float  # Великі тверді частинки (PM10) у мкг/м³
    aqi: int  # Індекс якості повітря (0-500)
    gps: Gps  # Розташування датчика
    humidity: float  # Відносна вологість у відсотках
    temperature: float  # Температура у градусах Цельсія
    timestamp: datetime
