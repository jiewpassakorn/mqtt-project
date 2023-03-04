# python 3.6

import random
import time
import pandas as pd
import uuid
from paho.mqtt import client as mqtt_client
import socket
from decouple import config


IP_ADDRESS = socket.gethostbyname(socket.gethostname())
MAX_PACKET_SIZE = 250
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "python/mqtt-ohm"
# generate client ID with pub prefix randomly
CLIENT_ID = f"python-mqtt-{random.randint(0, 1000)}"
USERNAME = "emqx"
PASSWORD = "public"


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            print(IP_ADDRESS)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    return client


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("unexpected to disconnect, return code %d\n", rc)
    else:
        print("disconnect success")


def read_sensor_data():
    # Read sensor data from Excel file
    df = pd.read_excel("SampleInput.xlsx")
    return df.to_dict("records")


def publish(client):
    sensor_data = read_sensor_data()
    for i, data in enumerate(sensor_data):
        data_id = str(uuid.uuid4())
        time.sleep(0.5)
        msg = str(data)
        packets = [
            msg[i: i + MAX_PACKET_SIZE] for i in range(0, len(msg), MAX_PACKET_SIZE)
        ]

        for j, packet in enumerate(packets):
            time.sleep(0.3)
            result = client.publish(
                TOPIC, f"{IP_ADDRESS}, {data_id}, {j}, {packet}")
            status = result[0]
            if status == 0:
                print(f"Sent {packet} to topic {TOPIC} ({i}, {j})")
            else:
                print(f"Failed to send message to topic {TOPIC}")

        time.sleep(0.5)
        client.publish(TOPIC, f"{IP_ADDRESS}, {data_id}, -1, end")

    time.sleep(0.5)
    client.publish(TOPIC, ",,,enddEIEI")
    print("endEIEI")


def run():
    client = connect_mqtt()
    publish(client)
    client.on_disconnect = on_disconnect
    client.disconnect()


if __name__ == "__main__":

    run()
