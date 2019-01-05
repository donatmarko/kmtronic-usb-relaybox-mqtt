__author__ = "Donat Marko"
__copyright__ = "Copyright 2018, Donatus"
__credits__ = ["Donat Marko"]
__license__ = "GPL-3.0"

import serial
import time
import random 
from config import *
import paho.mqtt.client as mqtt

# Array that stores the relays' statuses
relaystates=[False, False, False, False, False, False, False, False]

lwt_topic="tele/"+mqtt_topic+"/LWT"     # Birth/Last Will topic name
cmd_topic="cmnd/"+mqtt_topic+"/POWER"   # Command topic name
state_topic="stat/"+mqtt_topic+"/POWER" # State topic name
lwt_online="Online"         # Birth message
lwt_offline="Offline"       # Last Will and Testament message
cmd_on="ON"                 # "On" command          
cmd_off="OFF"               # "Off" command
cmd_toggle="TOGGLE"         # "Toggle" command

# We connect to the COM port on-demand.
def serialconnect():
    ser=serial.Serial()
    try:
        ser = serial.Serial(serial_port)
        print("Opening serial port " + ser.name)
    except:
        print("Unable to open the serial port. Maybe you are not admin/root (and you would need to be)")
    return ser

# We need to reset the relays (i.e. switch them off) upon startup as the module does NOT store (neither return) the states.
def relayinit():
    ser=serialconnect()
    ser.write(serial.to_bytes([0xFF,0x00,0x00]))
    time.sleep(0.05)

    # Setting the relay states as retained message
    for i in range(0, relays_count+1):
        statetopic=state_topic+("" if i==0 else str(i))
        if i==0:
            i=1
        off(i)
        client.publish(statetopic, state(i), 1, True)
    print("Relays reset.")

# Relay on
def on(relay):
    print("Relay "+str(relay)+" ON")
    ser=serialconnect()
    ser.write(serial.to_bytes([0xFF,relay,0x01]))
    time.sleep(0.05)
    relaystates[relay-1]=True
    
# Relay off
def off(relay):
    print("Relay "+str(relay)+" OFF")
    ser=serialconnect()
    ser.write(serial.to_bytes([0xFF,relay,0x00]))
    time.sleep(0.05)
    relaystates[relay-1]=False
    
# Relay toggle
def toggle(relay):
    print("Relay "+str(relay)+" TOGGLE")
    relaystates[relay-1]=not(relaystates[relay-1])
    ser=serialconnect()
    ser.write(serial.to_bytes([0xFF,relay, 0x01 if relaystates[relay-1] else 0x00 ]))
    time.sleep(0.05)

# Returns relay status as string
def state(relay):
    return cmd_on if relaystates[relay-1] else cmd_off

def on_disconnect(client, userdata, rc):
    print("Disconnected")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Publishing retained Birth message
    client.publish(lwt_topic, lwt_online, 1, True)
    # Subscribing to the necessary amount of command topics
    for i in range(0, relays_count+1):
        topic=cmd_topic+("" if i==0 else str(i))
        client.subscribe(topic)
        print("Subscribed to "+topic)

def on_message(client, userdata, msg):
    message=msg.payload.decode().upper()
    print("New message ["+msg.topic+"] = "+message)

    for i in range(0, relays_count+1):
        cmdtopic=cmd_topic+("" if i==0 else str(i))
        statetopic=state_topic+("" if i==0 else str(i))
        # Handling POWER equal to POWER1
        if i==0:
            i=1

        if msg.topic==cmdtopic:
            print(message)
            if cmd_on in message:
                on(i)
            if cmd_off in message:
                off(i)
            if cmd_toggle in message:
                toggle(i)
            client.publish(statetopic, state(i), 1, True)


print("DonatuSoft MQTT middleware for KMTronic USB relay boxes. www.donatus.hu. 2018.")

client = mqtt.Client(client_id=mqtt_topic+"-"+str(random.randint(100000,999999)))
client.on_connect=on_connect
client.on_message=on_message
client.on_disconnect=on_disconnect
client.username_pw_set(mqtt_username, mqtt_password)
client.will_set(lwt_topic, lwt_offline, 1, True)
relayinit()

try:
    print("Connecting to MQTT broker: "+mqtt_host)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
except KeyboardInterrupt:
    # Publishing retained last will message on exit - normally not being sent on proper discnnection
    client.publish(lwt_topic, lwt_offline, 1, True)
    client.disconnect()
