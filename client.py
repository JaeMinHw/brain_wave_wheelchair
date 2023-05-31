import socketio
import serial

port = "/dev/ttyACM0"
ard = serial.Serial(port,9600)


sio = socketio.Client()



@sio.event
def connect() :
	print('Connect to server')

@sio.on('order')
def order(data):
	print('Received response:',data)
	if data == 'go':
		s = '1'
		print("let's get it")
		ard.write(s.encode())

	elif data == 'back':
		s = '2'
		ard.write(s.encode())
	elif data == 'right':
		s = '3'
		ard.write(s.encode())

@sio.on('response')
def response(data):
	print(data)

if __name__ == '__main__' :
	sio.connect('http://43.200.191.244:5000')
