# python3.6

import random

from paho.mqtt import client as mqtt_client

import mysql.connector


USER = "root"
DB_NAME = "test"
PASSWORD = ""

TABLE_NAME = "sensor_data2"


broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        # timestamp, temperature, humidity,thermalarray = payload.split(',',3)
        # print(timestamp)
        # print(temperature)
        # print(humidity)
        # print(thermalarray)


        x = payload.split(',', 3)
        timestamp = x[0].split(':', 1)
        temperature = x[1].split(':', 1)
        humidity = x[2].split(':', 1)
        thermalarray = x[3].split(':', 1)

        print(str(timestamp[1].strip()), str(temperature[1].strip()), str(
            humidity[1].strip()), str(thermalarray[1][2:len(thermalarray[1])-2]))
        

        insert_to_database(str(timestamp[1][12:len(timestamp[1])-2]), float(temperature[1].strip()), float(
            humidity[1].strip()), str(thermalarray[1][2:len(thermalarray[1])-2]))
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def insert_to_database(timestamp, temperature, humidity,thermalarray):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=USER,
            password=PASSWORD,
            database=DB_NAME,
        )

        with connection.cursor() as cursor:
            sql = f"INSERT INTO `{TABLE_NAME}` (time, humidity, temperature, thermal_array) VALUES (%s, %s, %s, %s)"
            values = (timestamp, humidity, temperature, thermalarray)
            cursor.execute(sql, values)
        connection.commit()
    except Exception as e:
        print(f"Failed to write to MySQL database: {e}")
    finally:
        connection.close()


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
