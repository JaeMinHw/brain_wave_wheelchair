import socketio
import serial

port = "/dev/ttyACM0"
ard = serial.Serial(port,9600)

import RPi.GPIO as gpio
import time
 
TRIGER = 24
ECHO = 23
 
gpio.setmode(gpio.BCM)
gpio.setup(TRIGER, gpio.OUT)
gpio.setup(ECHO, gpio.IN)


sio = socketio.Client()


# after distance detect, if distance is too close, s = '7' ard.write(s.encode()) 



@sio.event
def connect() :
    print('Connect to server')
    

@sio.on('order')
def order(data):
    print('Received response:',data)
    move(data)
    # https://blog.naver.com/PostView.nhn?blogId=simjk98&logNo=221223898102
    sen1= Cal_distance()
    sen1.cal_distance(TRIGER,ECHO)


# https://hemon.tistory.com/72
class Cal_distance:
    def cal_distance(self,TRIGER,ECHO) :
        try:
            while True:
                gpio.output(TRIGER, gpio.LOW)
                time.sleep(0.1)
                gpio.output(TRIGER, gpio.HIGH)
                time.sleep(0.00002)
                gpio.output(TRIGER, gpio.LOW)

                while gpio.input(ECHO) == gpio.LOW:
                    startTime = time.time()   # 1sec unit

                while gpio.input(ECHO) == gpio.HIGH:
                    endTime = time.time()

                period = endTime - startTime
                dist1 = round(period * 1000000 / 58, 2)
                dist2 = round(period * 17241, 2)

                print("Dist1", dist1, "cm", ", Dist2", dist2, "cm")
                
                if dist1 < 10 and dist2 < 10:
                    move("stop")
                    print("detect")
                    self.join()
            
        except:
            gpio.cleanup()  


def move(data) :
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

    elif data == 'left':
        s = '4'
        ard.write(s.encode())

    elif data == 'Turning_rigth':
        s = '5'
        ard.write(s.encode())
    elif data == 'Turning_left':
        s = '6'
        ard.write(s.encode())
    elif data == 'stop':
        s = '7'
        ard.write(s.encode())

@sio.on('response')
def response(data):
    print(data)


if __name__ == '__main__' :
    sio.connect('http://43.200.191.244:5000')