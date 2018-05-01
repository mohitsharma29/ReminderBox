import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time

mqttc = mqtt.Client()
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()
print("Sending 0...")
publish.single("ledStatus", "0")
time.sleep(1)
print("Sending 1...")
publish.single("ledStatus", "1")