import csv
from datetime import datetime
from typing import Optional, TextIO, List

from domain.accelerometer import Accelerometer
from domain.air_quality import AirQuality
from domain.gps import Gps
from domain.aggregated_agent_data import AggregatedAgentData
import config


class AgentFileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename

        self.is_reading = False

        self.acc_file: Optional[TextIO] = None
        self.gps_file: Optional[TextIO] = None

        self.acc_reader: Optional[csv.DictReader] = None
        self.gps_reader: Optional[csv.DictReader] = None

    def read(self) -> AggregatedAgentData:
        """Метод повертає дані отримані з датчиків"""
        if not self.is_reading:
            raise RuntimeError("startReading() must be called before reading data")

        if not self.acc_reader or not self.gps_reader:
            raise RuntimeError("File readers not initialized")

        acc_row = next(self.acc_reader, None)
        gps_row = next(self.gps_reader, None)

        if acc_row is None:
            self._rewind_acc_file()
            acc_row = next(self.acc_reader)

        if gps_row is None:
            self._rewind_gps_file()
            gps_row = next(self.gps_reader)

        acc_data = Accelerometer(
            x=int(acc_row["x"]), y=int(acc_row["y"]), z=int(acc_row["z"])
        )

        gps_data = Gps(
            longitude=float(gps_row["longitude"]), latitude=float(gps_row["latitude"])
        )

        return AggregatedAgentData(
            accelerometer=acc_data,
            gps=gps_data,
            timestamp=datetime.now(),
            user_id=config.USER_ID,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.acc_file = open(self.accelerometer_filename, "r")
        self.gps_file = open(self.gps_filename, "r")

        self.acc_reader = csv.DictReader(self.acc_file)
        self.gps_reader = csv.DictReader(self.gps_file)

        self.is_reading = True

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.is_reading = False

        if self.acc_file:
            self.acc_file.close()
            self.acc_file = None
            self.acc_reader = None

        if self.gps_file:
            self.gps_file.close()
            self.gps_file = None
            self.gps_reader = None

    def _rewind_acc_file(self):
        """Скидання потоку файлу акселерометра на початок для реалізації нескінченного читання"""
        if self.acc_file:
            self.acc_file.seek(0)
            self.acc_reader = csv.DictReader(self.acc_file)

    def _rewind_gps_file(self):
        """Скидання потоку файлу GPS на початок для реалізації нескінченного читання"""
        if self.gps_file:
            self.gps_file.seek(0)
            self.gps_reader = csv.DictReader(self.gps_file)

    def __del__(self):
        """Деструктор для закриття файлів"""
        self.stopReading()


class AirQualityFileDatasource:
    def __init__(self, filename: str, batch_size: int = 5) -> None:
        self.air_quality_filename = filename

        self.batch_size = batch_size
        self.is_reading = False

        self.file: Optional[TextIO] = None
        self.reader: Optional[csv.DictReader] = None

    def read(self) -> List[AirQuality]:
        """Метод повертає пакет даних про якість повітря"""
        if not self.is_reading:
            raise RuntimeError("startReading() must be called before reading data")

        if not self.reader:
            raise RuntimeError("File reader not initialized")

        batch_data = []

        # Читаємо batch_size рядків
        for _ in range(self.batch_size):
            row = next(self.reader, None)

            if row is None:
                self._rewind_file()
                row = next(self.reader)

            air_quality = AirQuality(
                pm25=float(row["pm25"]),
                pm10=float(row["pm10"]),
                aqi=int(row["aqi"]),
                gps=Gps(
                    longitude=float(row["longitude"]), latitude=float(row["latitude"])
                ),
                humidity=float(row["humidity"]),
                temperature=float(row["temperature"]),
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
            )

            batch_data.append(air_quality)

        return batch_data

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.file = open(self.air_quality_filename, "r")
        self.reader = csv.DictReader(self.file)
        self.is_reading = True

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.is_reading = False
        if self.file:
            self.file.close()
            self.file = None
            self.reader = None

    def _rewind_file(self):
        """Скидання потоку файлу на початок для реалізації нескінченного читання"""
        if self.file:
            self.file.seek(0)
            self.reader = csv.DictReader(self.file)

    def __del__(self):
        """Деструктор для закриття файлу"""
        self.stopReading()
