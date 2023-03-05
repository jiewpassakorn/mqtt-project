# Import necessary libraries
import random  # For generating random numbers
import mysql.connector  # For connecting to MySQL database
import paho.mqtt.client as mqtt  # For MQTT communication
import os  # For loading environment variables
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()
USER = os.getenv("USER")
DB_NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("PASSWORD")
TABLE_NAME = os.getenv("TABLE_NAME")

# MQTT Broker configuration
broker = "broker.emqx.io"
port = 1883
topic = [("python/mqtt-kana", 0),
         ("python/mqtt-ohm", 0),
         ("python/mqtt-jiew", 0),
         ("python/mqtt-stang", 0)]

# Generate a random client ID with "python-mqtt-" prefix
client_id = f"python-mqtt-{random.randint(0, 100)}"

# MQTT Broker credentials
username = "emqx"
password = "public"

# Create a dictionary to store messages received from each unique device ID
global_dict = {}

# MQTT client callback function for when it successfully connects to the MQTT Broker


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # print("status            uid_packets                          ip_address")
    else:
        print(f"Failed to connect, return code {rc}\n")

# MQTT client callback function for when it receives a message from a subscribed topic


def on_message(client, userdata, msg):
    if msg.payload.decode("utf-8") == "1":  # flag 1 is connect
        print("================================")
        print(f"### {msg.topic} connected")

    elif msg.payload.decode("utf-8") == "0":  # flag 0 is disconnect
        print(f"### {msg.topic} disconnected")
        print("================================")
    else:
        # Decode message payload
        # print(msg.payload.decode("utf-8"))
        payload = msg.payload.decode()

        # Split payload into IP address, UID, index, and message parts
        ip_address, uid, index, message = payload.split(",", 3)

        # Strip whitespace from message part
        message = message.strip()

        # Add message to dictionary for that UID
        add_value(ip_address.strip(), uid, index, message, msg.topic)

# Function to connect to MQTT Broker


def connect_mqtt() -> mqtt.Client:
    # Create MQTT client object
    client = mqtt.Client(client_id)

    # Set MQTT client username and password
    client.username_pw_set(username, password)

    # Set MQTT client callback function for when it successfully connects to the MQTT Broker
    client.on_connect = on_connect

    # Connect to MQTT Broker
    client.connect(broker, port)

    return client

# Function to subscribe to a topic on the MQTT Broker


def subscribe(client: mqtt.Client):
    # Subscribe to the topic
    client.subscribe(topic)

    # Set MQTT client callback function for when it receives a message from a subscribed topic
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
    # insert_to_database(topic, timestamp,
    #                    temperature, humidity, thermalarray, uid)


def insert_to_database(topic, timestamp, temperature, humidity, thermalarray, uid):

    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user=USER,
            database=DB_NAME,
            password=PASSWORD
        )

        with connection.cursor() as cursor:
            topic = topic.split("/", 1).strip()
            # SQL statement to insert data into table
            sql = f"INSERT INTO `{TABLE_NAME}` (sensor_name, time, humidity, temperature, thermal_array) VALUES (%s, %s, %s, %s, %s)"
            values = (topic, timestamp, humidity, temperature, thermalarray)
            # Execute the SQL statement
            cursor.execute(sql, values)

        # Commit the changes
        connection.commit()
        # Print message indicating the insert was completed
        print("Insert completed", uid)
    except Exception as e:
        # Print error message if there was an exception
        print(f"Failed to write to MySQL database: {e}")
    finally:
        # Close the connection to the database
        connection.close()


def run():
    client = connect_mqtt()
    try:
        subscribe(client)
        client.loop_forever()
    except KeyboardInterrupt:
        print("KeyBoardInterrupt")


if __name__ == "__main__":
    run()
