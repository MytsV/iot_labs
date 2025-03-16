import os

import serial
import paho.mqtt.client as mqtt
import json
import datetime

from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.environ.get("MQTT_BROKER") or "localhost"
MQTT_PORT = int(os.environ.get("MQTT_PORT")) or 1883
MQTT_TOPIC = "agent_data_topic"

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
USER_ID = 0  # Default user ID


def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print(f"Connected to {SERIAL_PORT}")

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()

                try:
                    x, y, z = map(float, line.split(','))

                    # Create data in the requested format
                    data = {
                        "gyroscope": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "timestamp": datetime.datetime.now().isoformat(),
                        "user_id": USER_ID
                    }

                    # Convert to JSON string
                    data_json = json.dumps(data)

                    client.publish(MQTT_TOPIC, data_json)

                except ValueError as e:
                    print(f"Error parsing data: {line}")
                    continue

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        if 'ser' in locals():
            ser.close()


if __name__ == "__main__":
    main()
