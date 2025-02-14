import threading

from paho.mqtt import client as mqtt_client
import time
from schema.aggregated_agent_data_schema import AggregatedAgentDataSchema
from file_datasource import AgentFileDatasource, AirQualityFileDatasource
import config
from schema.air_quality_schema import AirQualitySchema


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish_agent(client, topic, datasource, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        data = datasource.read()
        msg = AggregatedAgentDataSchema().dumps(data)
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            pass
        else:
            print(f"Failed to send message to topic {topic}")


def publish_air_quality(client, topic, datasource, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        data_batch = datasource.read()
        for data in data_batch:
            msg = AirQualitySchema().dumps(data)
            result = client.publish(topic, msg)
            status = result[0]
            if status != 0:
                print(f"Failed to send message to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    # Prepare datasource
    agent_datasource = AgentFileDatasource("data/accelerometer.csv", "data/gps.csv")
    air_quality_datasource = AirQualityFileDatasource("data/air_quality.csv")

    agent_thread = threading.Thread(
        target=publish_agent,
        args=(client, config.MQTT_AGENT_TOPIC, agent_datasource, config.DELAY),
        daemon=True,
    )

    air_quality_thread = threading.Thread(
        target=publish_air_quality,
        args=(
            client,
            config.MQTT_AIR_QUALITY_TOPIC,
            air_quality_datasource,
            config.DELAY,
        ),
        daemon=True,
    )

    agent_thread.start()
    air_quality_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping the publishers...")


if __name__ == "__main__":
    run()
