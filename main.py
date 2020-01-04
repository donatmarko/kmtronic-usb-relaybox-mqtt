__author__ = "Donat Marko"
__copyright__ = "2020 Donat Marko | www.donatus.hu"
__credits__ = ["Donat Marko"]
__license__ = "GPL-3.0"
__version__ = "1.1.0"

import serial
import time
import random 
import json
import uuid
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

# Gets an (almost) permanent ID from MAC address to idenfity the client 
def get_uuid():
	mac_num = hex(uuid.getnode()).replace('0x', '').replace('L', '')
	mac_num = mac_num.zfill(12)
	mac = ''.join(mac_num[i : i + 2] for i in range(0, 11, 2))
	return mac[6:]

# We connect to the COM port on-demand.
def serialconnect():
    ser=serial.Serial()
    try:
        ser=serial.Serial(serial_port)
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
        mqtt_publish(client, statetopic, state(i), True)
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

def mqtt_publish(client, topic, payload, retain):
    client.publish(topic, payload, 1, retain)
    print("["+topic+"] "+payload+(" (retained)" if retain else ""))

# Purges discovery topics
def purge_discovery(client):
    for i in range(1, relays_count+1):
        topic=mqtt_discovery_prefix+"/switch/"+get_uuid()+"_"+str(i)+"/config"
        mqtt_publish(client, topic, "", True)

# Sends MQTT discovery messages
def send_discovery(client):
    for i in range(1, relays_count+1):
        topic=mqtt_discovery_prefix+"/switch/"+get_uuid()+"_"+str(i)+"/config"
        payload = {
            "name": "KMTronic "+str(i),
            "cmd_t": cmd_topic+str(i),
            "stat_t": state_topic+str(i),
            "pl_off": "OFF",
            "pl_on": "ON",
            "avty_t": lwt_topic,
            "pl_avail": "Online",
            "pl_not_avail": "Offline",
            "uniq_id": get_uuid()+"_"+str(i),
            "device": {
                "identifiers": [
                    get_uuid()
                ],
                "name": "KMTronic "+str(relays_count)+"-relay USB Relay Box",
                "model": "with Python MQTT middleware",
                "sw_version": __version__,
                "manufacturer": __author__
            }
        }     
        # mqtt_publish(client, topic, json.dumps(payload), True)
        # Not retaining only for dev purposes
        mqtt_publish(client, topic, json.dumps(payload), False)

def on_disconnect(client, userdata, rc):
    print("Disconnected")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Publishing retained Birth message
    mqtt_publish(client, lwt_topic, lwt_online, True)
    # Initializing relays - switch them off
    relayinit()
    # Purging previously retained MQTT discovery messages
    purge_discovery(client)
    # Sending MQTT discovery messages if enabled
    if mqtt_discovery:
        send_discovery(client)
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
            if cmd_on in message:
                on(i)
            if cmd_off in message:
                off(i)
            if cmd_toggle in message:
                toggle(i)
            mqtt_publish(client, statetopic, state(i), True)


print("DonatuSoft MQTT middleware for KMTronic USB relay boxes. www.donatus.hu. 2018.")

client = mqtt.Client(client_id=mqtt_topic+"-"+get_uuid())
client.on_connect=on_connect
client.on_message=on_message
client.on_disconnect=on_disconnect
client.username_pw_set(mqtt_username, mqtt_password)
client.will_set(lwt_topic, lwt_offline, 1, True)

try:
    print("Connecting to MQTT broker: "+mqtt_host)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()
except KeyboardInterrupt:
    # Publishing retained last will message on exit - normally not being sent on proper disconnection
    mqtt_publish(client, lwt_topic, lwt_offline, True)
    client.disconnect()
