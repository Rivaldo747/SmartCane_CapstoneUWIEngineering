import RPi.GPIO as GPIO

import time



# GPIO mode and pins

GPIO.setmode(GPIO.BCM)

flame_sensor_pin = 21  # GPIO pin connected to the flame sensor

buzzer_pin = 17  # GPIO pin connected to the buzzer



# Setup GPIO pins

GPIO.setup(flame_sensor_pin, GPIO.IN)

GPIO.setup(buzzer_pin, GPIO.OUT)



try:

    while True:

        if GPIO.input(flame_sensor_pin) == GPIO.LOW:  # Flame detected

            print("Flame detected!")

            GPIO.output(buzzer_pin, GPIO.HIGH)  # Turn on the buzzer

            time.sleep(1)  # Buzzer activation time

        else:

            print("No flame detected.")

            GPIO.output(buzzer_pin, GPIO.LOW)  # Turn off the buzzer when no flame is detected

        time.sleep(0.5)  # Check for flame every 0.5 seconds

 

except KeyboardInterrupt:

    GPIO.cleanup()  # keyboard interrupt

