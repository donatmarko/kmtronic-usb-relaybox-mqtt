# MQTT middleware for KMTronic USB relay boxes
> Python3 middleware for KMTronic USB 8 channel relay boxes to control the relays remotely with MQTT messages.

## What is it for?
This middleware has been developed for the **KMTronic USB Relay Controller Eight Channel** model to control the relays remotely and to make it controllable by various home automation systems, such as Home-Assistant.

It utilizes the Paho MQTT client to connect to any MQTT broker, and makes it possible to turn on/off the relays with simple messages.

## Installation and running
1. Install the requirements:

   `python -m pip install -r requirements.txt`

2. Copy `config.sample.py` to `config.py` and fill the variables.

3. Run the middleware:

   `python main.py`
   
4. Done :)

## Topics and commands
Topic                  | Direction       | Purpose
---------------------- | --------------- | -----------------------------------------------------
cmnd/*TOPIC*/POWER{id} | to middleware   | Controls the specified relay (ON/OFF/TOGGLE)
stat/*TOPIC*/POWER{id} | from middleware | Returns the state of the relay (ON/OFF)
tele/*TOPIC*/LWT       | from middleware | Returns the status of the middleware (Online/Offline)

## Bugreport, feature request?
Create a new issue at GitHub and I will do my best with.

## Warranty?
No.
