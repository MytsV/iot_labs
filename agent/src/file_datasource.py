import csv
from datetime import datetime
from typing import Optional, TextIO

from domain.gyroscope import Gyroscope
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(
        self,
        gyroscope_filename: str,
        gps_filename: str,
    ) -> None:
        self.gyroscope_filename = gyroscope_filename
        self.gps_filename = gps_filename

        self.is_reading = False

        self.gyro_file: Optional[TextIO] = None
        self.gps_file: Optional[TextIO] = None

        self.gyro_reader: Optional[csv.DictReader] = None
        self.gps_reader: Optional[csv.DictReader] = None

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        if not self.is_reading:
            raise RuntimeError("startReading() must be called before reading data")

        if not self.gyro_reader or not self.gps_reader:
            raise RuntimeError("File readers not initialized")

        gyro_row = next(self.gyro_reader, None)
        gps_row = next(self.gps_reader, None)

        if gyro_row is None:
            self._rewind_acc_file()
            gyro_row = next(self.gyro_reader)

        if gps_row is None:
            self._rewind_gps_file()
            gps_row = next(self.gps_reader)

        gyro_data = Gyroscope(
            x=int(gyro_row["x"]), y=int(gyro_row["y"]), z=int(gyro_row["z"])
        )

        gps_data = Gps(
            longitude=float(gps_row["longitude"]), latitude=float(gps_row["latitude"])
        )

        return AggregatedData(
            gyroscope=gyro_data,
            gps=gps_data,
            timestamp=datetime.now(),
            user_id=config.USER_ID,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.gyro_file = open(self.gyroscope_filename, "r")
        self.gps_file = open(self.gps_filename, "r")

        self.gyro_reader = csv.DictReader(self.gyro_file)
        self.gps_reader = csv.DictReader(self.gps_file)

        self.is_reading = True

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.is_reading = False

        if self.gyro_file:
            self.gyro_file.close()
            self.gyro_file = None
            self.gyro_reader = None

        if self.gps_file:
            self.gps_file.close()
            self.gps_file = None
            self.gps_reader = None

    def _rewind_acc_file(self):
        """Скидання потоку файлу акселерометра на початок для реалізації нескінченного читання"""
        if self.gyro_file:
            self.gyro_file.seek(0)
            self.gyro_reader = csv.DictReader(self.gyro_file)

    def _rewind_gps_file(self):
        """Скидання потоку файлу GPS на початок для реалізації нескінченного читання"""
        if self.gps_file:
            self.gps_file.seek(0)
            self.gps_reader = csv.DictReader(self.gps_file)

    def __del__(self):
        """Деструктор для закриття файлів"""
        self.stopReading()
