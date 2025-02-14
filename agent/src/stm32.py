import serial
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "stm32/gyroscope"

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200


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

                    data = f'{{"x": {x}, "y": {y}, "z": {z}}}'

                    client.publish(MQTT_TOPIC, data)

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
