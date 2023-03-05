# python3.6

import random

from paho.mqtt import client as mqtt_client

import mysql.connector


USER = "root"
DB_NAME = "test"
PASSWORD = "Jiew_1125"

TABLE_NAME = "sensor_data2"


broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt-jiew"
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
        
        data = payload.split(',', 3)
        timestamp = data[0].split(':', 1)[1].strip()
        temperature = float(data[1].split(':',1)[1].strip())
        humidity = float(data[2].split(':',1)[1].strip())
        thermalarray = data[3].split(':',1)[1].strip()[1:-2]
       
           
        timestamp_val = timestamp.split("'")
        timestamp=timestamp_val[1]

        print(timestamp, temperature, humidity, thermalarray)  
        insert_to_database(timestamp, temperature, humidity, thermalarray)
        
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def insert_to_database(timestamp, temperature, humidity, thermalarray):
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
