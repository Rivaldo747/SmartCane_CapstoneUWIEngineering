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

def play_sound():
    subprocess.run(["pico2wave", "-w", "object_detected.wav", "Object detected near the LIDAR sensor"], check=True)
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
lines = list()
angles = list()
distances = list()

i = 0
while True:
    loopFlag = True
    flag2c = False

    if i % 40 == 39:
        if 'line' in locals():
            line.remove()
        line = ax.scatter(angles, distances, c="pink", s=5)

        ax.set_theta_offset(math.pi / 2)
        plt.pause(0.01)
        angles.clear()
        distances.clear()
        i = 0

    while loopFlag:
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
                continue

            lidarData = CalcLidarData(tmpString[0:-5])
            angles.extend(lidarData.Angle_i)
            distances.extend(lidarData.Distance_i)

            for angle, distance in zip(lidarData.Angle_i, lidarData.Distance_i):
                print(f"Angle: {angle:.2f} degrees, Distance: {distance:.2f} cm")
                if distance < 1200:  # 12 meters in cm
                    trigger_buzzer()
                    play_sound()
                else:
                    os.remove("object_detected.wav")

            tmpString = ""
            loopFlag = False
        else:
            tmpString += b.hex() + " "

        flag2c = False

    i += 1

ser.close()
GPIO.cleanup()
