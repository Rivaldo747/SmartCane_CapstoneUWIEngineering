import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
#ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.flushInput()

phone_number = '8768977813'
power_key = 6
button_pin = 22 
rec_buff = ''

def send_at(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	if back not in rec_buff.decode():
		print(command + ' ERROR')
		print(command + ' back:\t' + rec_buff.decode())
		return 0
	else:
		print(rec_buff.decode())
		return 1

def power_on(power_key):
	print('SIM7600X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #button pin set as input with pull-up resistor
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(20)
	ser.flushInput()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is loging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	print('Good bye')

try:
	power_on(power_key)
	
	while True:
		if GPIO.input(button_pin) == GPIO.LOW:  # Button is pressed
			send_at('ATD'+phone_number+';','OK',1)
			time.sleep(20)
			ser.write('AT+CHUP\r\n'.encode())
			print('Call disconnected')
			break  # Exit the loop after the call is made
		time.sleep(0.1)  
		
	power_down(power_key)
except :
    if ser != None:
        ser.close()
        GPIO.cleanup()

if ser != None:
	ser.close()
	GPIO.cleanup()
