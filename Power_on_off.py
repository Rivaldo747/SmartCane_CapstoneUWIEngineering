import RPi.GPIO as GPIO
import os
import time

# GPIO mode
GPIO.setmode(GPIO.BCM)

# GPIO pin 3 as input
GPIO.setup(3, GPIO.IN)

# Function to handle button press
def button_pressed(channel):
    global state
    state = not state
    if state:
        print("Shutting down SmartCane...")
        os.system("sudo shutdown -h now")
    else:
        print("Restarting SmartCane..")
        os.system("sudo reboot")

# falling edge on GPIO pin 3
GPIO.add_event_detect(3, GPIO.FALLING, callback=button_pressed, bouncetime=200)

# Initialize state
state = False

# Main loop
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
