import serial
import binascii
from CalcLidarData import CalcLidarData
import matplotlib.pyplot as plt
import math
import RPi.GPIO as GPIO
import subprocess
import os
import time

GPIO.setmode(GPIO.BCM)
BUZZER_PIN = 17
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def trigger_buzzer():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.5)  
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def play_sound(side):
    subprocess.run(["pico2wave", "-w", "object_detected.wav", f"Obstacle detected on the {side} side"], check=True)
    subprocess.run(["aplay", "object_detected.wav"], check=True)
    os.remove("object_detected.wav")

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='polar')
ax.set_title('lidar (exit: Key E)', fontsize=18)

plt.connect('key_press_event', lambda event: exit(1) if event.key == 'e' else None)

ser = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=230400,
                    timeout=5.0,
                    bytesize=8,
                    parity='N',
                    stopbits=1)

tmpString = ""
angles = []
distances = []

while True:
    loopFlag = True
    flag2c = False

    for i in range(40):
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')

        if tmpInt == 0x54:
            tmpString += b.hex() + " "
            flag2c = True
            continue

        elif tmpInt == 0x2c and flag2c:
            tmpString += b.hex()

            if not len(tmpString[0:-5].replace(' ', '')) == 90:
                tmpString = ""
                loopFlag = False
                flag2c = False
                break

            lidarData = CalcLidarData(tmpString[0:-5])
            angles.extend(lidarData.Angle_i)
            distances.extend(lidarData.Distance_i)

            # Detect holes and obstacles
            for i, distance in enumerate(lidarData.Distance_i):
                if distance > 1200:  # Hole detection threshold (1200 cm = 12 meters)
                    print(f"Hole detected at angle {lidarData.Angle_i[i]:.2f} degrees")
                    if lidarData.Angle_i[i] < 180:
                        play_sound("left")
                    else:
                        play_sound("right")
                elif distance < 1000:  # Obstacle detection threshold (1000 cm = 10meters)
                    print(f"Obstacle detected at angle {lidarData.Angle_i[i]:.2f} degrees")
                    if lidarData.Angle_i[i] < 180:
                        play_sound("right")
                    else:
                        play_sound("left")

            tmpString = ""
            loopFlag = False
        else:
            tmpString += b.hex() + " "

        flag2c = False

ser.close()
GPIO.cleanup()

