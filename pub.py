# python 3.6

import random
import time
import pandas as pd
import uuid
from paho.mqtt import client as mqtt_client
import socket

ip_address = socket.gethostbyname(socket.gethostname())
MAX_PACKET_SIZE = 250
broker = 'broker.emqx.io'
port = 1883
topic = "python/mqtt-ohm"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            print(ip_address)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
def on_disconnect(client, userdata, rc):
    if rc != 0: 
        print("unexpected to disconnect, return code %d\n", rc)
    else :
        print("disconnect ok")
        
    

def read_sensor_data():
    # Read sensor data from Excel file
    df = pd.read_excel('SampleInput.xlsx')
    return df.to_dict('records')

def publish(client):
    
    sensor_data = read_sensor_data()
    msg_count = 0
    for i in range(len(sensor_data)):
        data_id = str(uuid.uuid4())
        time.sleep(0.5)
        msg = str(sensor_data[msg_count])
        packets = [msg[i:i+MAX_PACKET_SIZE] for i in range(0, len(msg), MAX_PACKET_SIZE)]
        
        for index,sending in enumerate(packets) :
            time.sleep(0.2)
            result = client.publish(topic, str(ip_address)+", "+data_id+", " +str(index) + ", " + sending)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{ip_address}` `{sending}` to topic `{topic}`  `{i}`")
            else:
                print(f"Failed to send message to topic {topic}")
        time.sleep(0.2)
        client.publish(topic,str(ip_address)+", "+ data_id+", " +"-1" + ", " + "end")
        msg_count += 1
    time.sleep(1)
    client.publish(topic, ",,,enddEIEI")
    print("endEIEI")
    
    
    

def run():
    client = connect_mqtt()
    publish(client)
    client.on_disconnect = on_disconnect
    client.disconnect()

if __name__ == '__main__':
    
    run()
    