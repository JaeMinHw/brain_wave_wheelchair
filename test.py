import serial
import time
import pyfirmata

port = "/dev/ttyACM0"
ard = serial.Serial(port,9600)

def write(data):
	if data == '1':
		s = '1'
		ard.write(s.encode())
	elif data == '2':
		s = '2'
		ard.write(s.encode())
	elif data == '3':
		s = '3'
		ard.write(s.encode())





time.sleep(6)
write("1")
time.sleep(6)
write("2")
time.sleep(6)
write("3")


