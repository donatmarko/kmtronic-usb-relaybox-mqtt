# MQTT middleware for KMTronic USB relay boxes

Python3 middleware for KMTronic USB relay boxes to control the relays remotely with MQTT messages.

## What is it for?

This middleware has been developed for the **KMTronic USB Relay Controller Eight Channel** model (but can be used with other boards with different number of relays) to control the relays remotely and to make it controllable by various home automation systems, such as Home-Assistant.

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

## Home-Assistant MQTT Discovery

From version 1.1.0 the middleware is able to add the relays without writing a single line of Home-Assistant configuration file by using the MQTT discovery technique.

Assuming you have MQTT discovery enabled in Home-Assistant, to activate this function in the middleware, set the `mqtt_discovery` parameter to `True` in the `config.py` file, and make sure that you use the same prefix in both software.

After restarting the middleware the relays must appear on your Home-Assistant dashboard.

## Bugreport, feature request?

Create a new issue at GitHub and I will do my best with.

## Warranty?

No.
