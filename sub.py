# python3.6

import random

from paho.mqtt import client as mqtt_client

import mysql.connector


USER = "root"
DB_NAME = "MQTT_PROJECT"
PASSWORD = "stank5843"

TABLE_NAME = "sensor_data"


broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt-ohm"
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

global_dict = {}
            
def split_and_insert(ip_address,uid,message) :
        data = message.split(',', 3)
        timestamp = data[0].split(':', 1)[1].strip().split("'",2)[1]
        temperature = float(data[1].split(':',1)[1].strip())
        humidity = float(data[2].split(':',1)[1].strip())
        thermalarray = data[3].split(':',1)[1].strip()[1:-2]
        #print(humidity)
        #print(timestamp, temperature, humidity)
        insert_to_database(ip_address,uid,timestamp, temperature, humidity, thermalarray)
        
def add_value(ip_address,uid,index,message) :
    
    if message == "end" :
        split_and_insert(ip_address,uid,global_dict[uid])
        del global_dict[uid]
        # if uid not in global_dict.keys() :
        #     print(f"deleted `{uid}`")
    else :
        if uid in global_dict.keys() :
            data = global_dict[uid] + message
            global_dict.update({uid : data})
        else:
            global_dict.update({uid : message})

def subscribe(client: mqtt_client):
   
    def on_message(client, userdata, msg):
         
        payload = msg.payload.decode()
        
        #print(payload)
        ip_address,uid, index, message = payload.split(",",3)
        message = message.strip()
            
        add_value(ip_address.strip(),uid,index,message)
        

    client.subscribe(topic)
    client.on_message = on_message


def insert_to_database(ip_address,uid,timestamp, temperature, humidity, thermalarray):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=USER,
            password=PASSWORD,
            database=DB_NAME,
        )

        with connection.cursor() as cursor:
            sql = f"INSERT INTO `{TABLE_NAME}` (ip_address, time, humidity, temperature, thermal_array) VALUES (%s,%s, %s, %s, %s)"
            values = (ip_address, timestamp, humidity, temperature, thermalarray)
            cursor.execute(sql, values)
        connection.commit()
        print("insert completed",uid,ip_address)
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