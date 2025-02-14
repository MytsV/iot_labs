import csv
import random
from datetime import datetime, timedelta
import math


def calculate_aqi(pm25, pm10):
    """Розрахунок наближеного індексу якості повітря на основі PM2.5 та PM10"""
    # Спрощена формула для демонстрації
    aqi = int((pm25 * 2.5 + pm10 * 0.5))
    return min(max(aqi, 0), 500)


def generate_mock_data(filename, num_records):
    """Генерація тестових даних датчика якості повітря"""

    # Базові координати (центр Києва)
    base_lat = 50.450386
    base_lon = 30.524547

    # Параметри для реалістичних коливань
    time_of_day = 0  # 0-24 для добового циклу

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "pm25",
                "pm10",
                "aqi",
                "longitude",
                "latitude",
                "humidity",
                "temperature",
                "timestamp",
            ]
        )

        for i in range(num_records):
            # Симуляція добового циклу (24 години)
            time_of_day = i % 24

            # Базові значення з добовими коливаннями
            time_factor = math.sin(time_of_day * math.pi / 12)  # Пік опівдні

            # PM2.5 (типовий діапазон 0-100 мкг/м³)
            pm25_base = 15 + time_factor * 5  # Більше забруднення вдень
            pm25 = round(max(0, pm25_base + random.uniform(-3, 3)), 1)

            # PM10 (типовий діапазон 0-150 мкг/м³)
            pm10_base = pm25 * 2.5 + time_factor * 10
            pm10 = round(max(0, pm10_base + random.uniform(-5, 5)), 1)

            # Розрахунок AQI
            aqi = calculate_aqi(pm25, pm10)

            # Координати з невеликим відхиленням
            lat = base_lat + random.uniform(-0.002, 0.002)
            lon = base_lon + random.uniform(-0.002, 0.002)

            # Температура (типовий діапазон 15-25°C з добовими коливаннями)
            temp_base = 20 + time_factor * 3
            temperature = round(temp_base + random.uniform(-1, 1), 1)

            # Вологість (типовий діапазон 40-80%)
            humidity_base = 60 - time_factor * 10
            humidity = round(max(40, min(80, humidity_base + random.uniform(-5, 5))), 1)

            # Часова мітка
            timestamp = (datetime.now() + timedelta(hours=i)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            writer.writerow(
                [pm25, pm10, aqi, lon, lat, humidity, temperature, timestamp]
            )


if __name__ == "__main__":
    generate_mock_data("../data/air_quality.csv", num_records=1000)
    print("Згенеровано тестові дані якості повітря у файлі air_quality.csv")
