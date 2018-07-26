#!/usr/bin/env python

# GPS module.
# Will wait for a fix and print a message every second with the current location
# and other details.
# Will send each message to Microsoft Azure ServiceBus in JSON format
import time, board, busio, json
import adafruit_gps


# Define RX and TX pins for the board's serial port connected to the GPS.
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
RX = GPS module TX
TX = GPS module RX

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
uart = busio.UART(TX, RX, baudrate = 9600, timeout = 4000)

# Create GPS Module instance
gps = adafruit_gps.GPS(uart)

# Turn on just minimum info (RMC only, location):
gps.send_command('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once every two seconds
gps.send_command('PMTK220,2000')

# Create Service Bus object
sbs = createSBS()

# Create ID for device
iD = getId()

last_print = time.monotonic()
while True:
    # Call gps.update() loop
    gps.update()
    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 5.0:
        last_print = current
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            print('Waiting for fix...')
            continue

        # We have a fix! (gps.has_fix is true)
        time = '{}/{}/{} {:02}:{:02}:{:02}'.format(
            gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
            gps.timestamp_utc.tm_mday,  # struct_time object that holds
            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
            gps.timestamp_utc.tm_hour,  # not get all data like year, day,
            gps.timestamp_utc.tm_min,   # month!
            gps.timestamp_utc.tm_sec
        )

        # Creates JSON message
        data = {
            'DeviceID': iD,
            'Latitude (degrees)': gps.latitude,
            'Longitude (degrees)': gps.longitude,
            'Fix Quality': gps.fix_quality,
            'Fix Timestamp': time
        }
        msg = json.dumps(data)

        # Print out details about the fix like location, date, etc.
        print('=' * 40)
        print(msg)

        # Send msg to ServiceBus using Queue name
	    sbs.send_event('rpi-device-data',msg)