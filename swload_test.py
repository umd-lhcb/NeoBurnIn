#!/usr/bin/env python3
#
# Author: Ben Flaggs

import RPi.GPIO as GPIO
import sys
import time

# Use rpi board numbering
GPIO.setmode(GPIO.BOARD)

# Take GPIO pin from user input
ch1 = int(sys.argv[1])
ch2 = int(sys.argv[2])

GPIO.setup(ch1, GPIO.OUT)
GPIO.setup(ch2, GPIO.OUT)


try:
    while True:
        print("Pulling GPIO pins {} and {} HIGH".format(ch1, ch2))
        GPIO.output(ch1, GPIO.HIGH)
        GPIO.output(ch2, GPIO.HIGH)
        time.sleep(60)

        print("Pulling GPIO pins {} and {} LOW".format(ch1, ch2))
        GPIO.output(ch1, GPIO.LOW)
        GPIO.output(ch2, GPIO.LOW)
        time.sleep(10)
except KeyboardInterrupt:
    print("Stopping test for switching load board.")

# Cleanup GPIO pins on pi
GPIO.cleanup()
