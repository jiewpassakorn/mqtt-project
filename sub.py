# Import necessary libraries
import random  # For generating random numbers
import mysql.connector  # For connecting to MySQL database
import paho.mqtt.client as mqtt  # For MQTT communication
import os  # For loading environment variables
from dotenv import load_dotenv  # For loading environment variables from .env file
import uuid

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
global_dict = {}

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

# Function to add a message to the dictionary for that UID


def add_value(ip_address, uid, index, message, topic):
    # If message is "end", split and insert the entire message for that UID into the database
    if message == "end":
        split_and_insert(ip_address, uid, global_dict[uid], topic)
        del global_dict[uid]
    else:
        # If the UID already exists in the dictionary, concatenate the new message to the existing message for that UID
        if uid in global_dict.keys():
            data = global_dict[uid] + message
            global_dict.update({uid: data})
        # If the UID does not exist in the dictionary, add the new message to the dictionary for that UID
        else:
            global_dict.update({uid: message})

# This function splits the incoming message into timestamp, temperature, humidity, and thermalarray parts and calls the insert_to_database function to store the data in the database.


def split_and_insert(ip_address, uid, message, topic):
    # Split message into timestamp, temperature, humidity, and thermalarray parts
    data = message.split(",", 3)
    timestamp = data[0].split(":", 1)[1].strip().split("'", 2)[1]
    temperature = float(data[1].split(":", 1)[1].strip())
    humidity = float(data[2].split(":", 1)[1].strip())
    thermalarray = data[3].split(":", 1)[1].strip()[1:-2]
    print(f"received {uid} from {topic}")
    # Call insert_to_database function to store data in database
    insert_to_database(topic, timestamp,
                       temperature, humidity, thermalarray,uid)

def insert_to_database(topic,timestamp, temperature, humidity, thermalarray, uid):

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
        # Print message indicating the insert was completed
        print("Insert completed",uid)
    except Exception as e:
        print(f"Failed to write to MySQL database: {e}")
    finally:
        connection.close()


def run():
    client = connect_mqtt()
    
    try:
        subscribe(client)
        client.loop_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

    
    


if __name__ == '__main__':
    run()
