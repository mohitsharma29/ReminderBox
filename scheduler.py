import schedule
import time
from datetime import datetime
import pytz
from models import initialize_db, Schedule
from random import randint
import paho.mqtt.client as mqttClient
from models import logs

#MQTT Connection details
broker_address= "m14.cloudmqtt.com"
port = 15735
user = "tkqzipqu"
password = "KPoN6BkcCC3c"

STD_TIMES = [14,20]

tz = pytz.timezone('Asia/Kolkata')

# Publisher Code
def on_connect_pub(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected_pub                #Use global variable
        Connected_pub = True                #Signal connection
    else:
        print("Connection failed")
Connected_pub = False   #global variable for the state of the connection

def send_mqtt(box, payloadMessage):
    client = mqttClient.Client("Python")  # create new instance
    client.username_pw_set(user, password=password)  # set username and password
    client.on_connect = on_connect_pub  # attach function to callback
    client.connect(broker_address, port=port)  # connect to broker
    client.loop_start()  # start the loop
    while Connected_pub != True:  # Wait for connection
        time.sleep(0.1)
    print(payloadMessage)
    client.publish(box, payloadMessage)
    client.disconnect()
    client.loop_stop()

#Subscribe Code
def on_connect_sub(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected_sub  # Use global variable
        Connected_sub = True  # Signal connection
    else:
        print("Connection failed")
Connected_sub = False   #global variable for the state of the connection

def on_message(client, userdata, message):
    logs.create(message = message.payload)
    print("Message received: "  + message.payload)

def receive_mqtt(box):
    client = mqttClient.Client("Python")  # create new instance
    client.username_pw_set(user, password=password)  # set username and password
    client.on_connect = on_connect_sub  # attach function to callback
    client.on_message = on_message  # attach function to callback
    client.connect(broker_address, port=port)  # connect to broker
    client.loop_start()  # start the loop
    while Connected_sub != True:  # Wait for connection
        time.sleep(0.1)
    client.subscribe(box)
    while True:
        time.sleep(1)

# Functions to send Reminders
def check():
    rand_flag = 0
    while True:
        if datetime.now(tz).hour == 0:
            rand_flag = 0
        schedules = Schedule.select()
        random_slot = [x for x in schedules if x.afterWhat == 'rm']
        before_slot = [x for x in schedules if x.afterWhat == 'bfm']
        after_slot = [x for x in schedules if x.afterWhat == 'afm']
        if datetime.now(tz).hour in STD_TIMES:
            for i in before_slot:
                tempBox = i.boxName
                tempMsg = "Take " + i.medicineName + " " + str(i.numTabs) + "Tabs."
                send_mqtt(tempBox, tempMsg)
        if datetime.now(tz).hour == randint(8,20) and rand_flag == 0:
            rand_flag = 1
            for i in random_slot:
                tempBox = i.boxName
                tempMsg = "Take " + i.medicineName + " " + str(i.numTabs) + "Tabs."
                send_mqtt(tempBox, tempMsg)
        if datetime.now(tz).hour in STD_TIMES and datetime.now(tz).minute >= 30 and datetime.now(tz).minute <= 40:
            for i in after_slot:
                tempBox = i.boxName
                tempMsg = "Take " + i.medicineName + " " + str(i.numTabs) + "Tabs."
                send_mqtt(tempBox, temp_Msg)