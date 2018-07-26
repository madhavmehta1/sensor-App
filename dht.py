#!/usr/bin/env python

# Simple temperature/humidity module.
# Will print temperature, humidity and other details.
# Will send each message to Microsoft Azure ServiceBus in JSON format
import sys, datetime, json
import Adafruit_DHT

from util import *

# Create Service Bus object
sbs = createSBS()

# Create ID for device
iD = getId()

# Get DHT11 sensor data, convert into JSON, and send data to ServiceBus
while True:	
	# Get Timestamp
	dt = str(datetime.datetime.now())

	# Get DHT Sensor data on from GPIO4
	humid, temp = Adafruit_DHT.read_retry(11, 4)

	# Convert C to F (Circumstantial need)
	# f = t * 9. / 5. + 32 # from C to F

	# Create JSON message
	data = {
	'DeviceID': iD,
	'Temperature': temp,
	'Humidity': humid,
	'Time': dt
	}
	msg = json.dumps(data)

	# Print JSON message for testing purposes
	print(msg)

	# Send msg to ServiceBus using Queue name
	sbs.send_event('rpi-device-data',msg)
