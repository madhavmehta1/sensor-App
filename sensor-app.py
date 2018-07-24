#!/usr/bin/python
import sys, datetime, json
import Adafruit_DHT, adafruit_gps
import time, busio

from util import *


RX = GPS module TX
TX = GPS module RX

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
uart = busio.UART(TX, RX, baudrate = 9600, timeout = 4000)

# Create GPS Module instance
gps = adafruit_gps.GPS(uart)

# Initialize GPS Module 


# Turn on just minimum info (RMC only, location):
gps.send_command('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once every two seconds
gps.send_command('PMTK220,2000')

# Create Service Bus object
sbs = createSBS()

# Create ID for device
iD = getId()

# Get Ultimate GPS sensor and DHT11 sensor data, convert into JSON, and send data to ServiceBus
last_Print = time.monotonic()
while True:	
	# Get Timestamp
	dt = str(datetime.datetime.now())

	# Get DHT Sensor data on from GPIO4
	humid, temp = Adafruit_DHT.read_retry(11, 4)

	# Convert C to F (Circumstantial need)
	# f = t * 9. / 5. + 32 # from C to F

	# Calling gps.update() loop 
	gps.update()
	# Print out current location details every 5 seconds if there is a fix on location
	current = time.monotonic()
	if current - last_Print >= 5.0:
		last_Print = current
		if gps.has_fix:
			continue
		loc = {
			'Latitude (degrees)': gps.latitude,
			'Longitude (degrees)': gps.longitude,
			'Speed over ground (knots)': gps.speed_knots,
			'Fix Quality': gps.fix_quality
		}

	# Create JSON message
	data = {
	'DeviceID': iD,
	'Temperature': temp,
	'Humidity': humid,
	'Time': dt,
	'Location': loc
	}
	msg = json.dumps(data)

	# Print JSON message for testing purposes
	print(msg)

	# Send msg to ServiceBus using Queue name
	sbs.send_event('rpi-device-data',msg)
