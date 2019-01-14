# Used serial port for the relay box
#    e.g. COM7
#         /dev/ttyACM0
serial_port="COM7"

# Relays count in the relay box
relays_count=8

# Middle part of the MQTT topics
#    most likely unique project names
#    Don't use full (e.g. cmnd/kmtronic/POWER) names!
mqtt_topic="kmtronic"

# Enables MQTT discovery for Home-Assistant to detect the relays automatically
mqtt_discovery=False
# Prefix for Home-Assistant MQTT discovery (by default "homeassistant")
mqtt_discovery_prefix="homeassistant"

# MQTT connection data
mqtt_host="192.168.0.1"
mqtt_port=1883
mqtt_username="mqtt"
mqtt_password="IWONTDISCLOSE"
