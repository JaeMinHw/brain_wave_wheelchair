import socketio
import serial
import threading
import websockets
import cv2
import base64
import os, sys
import asyncio
import requests
from ast import literal_eval
import aiohttp
port = "/dev/ttyACM0"
ard = serial.Serial(port,9600)

import RPi.GPIO as gpio
import time

import io
import numpy as np
from PIL import Image
 
TRIGER = 24
ECHO = 23

TRIGER2 = 27
ECHO2 = 22

TRIGER3 = 6
ECHO3 = 5

TRIGER4 = 25
ECHO4 = 17  

 




sio = socketio.Client()

# thread1 = threading.Thread()
# thread2 = threading.Thread()
# thread3 = threading.Thread()
# thread4 = threading.Thread()



# after distance detect, if distance is too close, s = '7' ard.write(s.encode()) 



@sio.event
def connect() :
    print('Connect to server')
    
thread1 = None
thread2 = None
thread3 = None
thread4 = None
x = None
y= None
z = None
k = None
@sio.on('order')
def order(data):
    

    print('Received response:', data)
    move(data)
    
    global x,y,z,k
    x = Cal_distance("t1", TRIGER, ECHO)
    y = Cal_distance("t2", TRIGER2, ECHO2)
    z = Cal_distance("t3", TRIGER3, ECHO3)
    k = Cal_distance("t4", TRIGER4, ECHO4)

    global thread1, thread2, thread3, thread4
    thread1 = threading.Thread(target=x.cal_distance)
    thread2 = threading.Thread(target=y.cal_distance)
    thread3 = threading.Thread(target=z.cal_distance)
    thread4 = threading.Thread(target=k.cal_distance)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

class Cal_distance:
    def __init__(self, name, TRIGER, ECHO):
        self.name = name
        self.TRIGER = TRIGER
        self.ECHO = ECHO
        self.dist1 = 0
        self.stop_event = threading.Event()

    def cal_distance(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.TRIGER, gpio.OUT)
        gpio.setup(self.ECHO, gpio.IN)

        try:
            while not self.stop_event.is_set():
                startTime = time.time()
                gpio.output(self.TRIGER, gpio.LOW)
                time.sleep(0.1)
                gpio.output(self.TRIGER, gpio.HIGH)
                time.sleep(0.00002)
                gpio.output(self.TRIGER, gpio.LOW)

                while gpio.input(self.ECHO) == gpio.LOW:
                    startTime = time.time()

                while gpio.input(self.ECHO) == gpio.HIGH:
                    endTime = time.time()

                period = endTime - startTime
                self.dist1 = round(period * 1000000 / 58, 2)

                

                if self.dist1 < 30:
                    print("", self.name, "Dist1", self.dist1, "cm")
                    move("stop")
                    requests.get('http://3.36.70.207/status/',self.name)


        except Exception as e:
            print("Error:", str(e))
            
            
    def stop(self):
        self.stop_event.set()  # stop_event 설정하여 쓰레드 종료


def move(data) :
    if data == 'go':
        gpio.setmode(gpio.BCM)
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
        print("2")
        ard.write(s.encode())
        s1 = '0'
        ard.write(s1.encode())
        
        # thread1.join()
        # thread2.join()
        # thread3.join()
        # thread4.join()
        # gpio.ouput(TRIGER,gpio.LOW)
        # gpio.ouput(TRIGER2,gpio.LOW)
        # gpio.ouput(TRIGER3,gpio.LOW)
        # gpio.ouput(TRIGER4,gpio.LOW)
    if x is not None :    
        print("sad")
        x.stop()
    if y is not None :
        y.stop()
    if z is not None :
        z.stop()
    if k is not None :
        k.stop()

@sio.on('response')
def response(data):
    print(data)





# 로컬 카메라 캡처 객체 생성
cap = cv2.VideoCapture(0)  # 0은 기본 카메라를 의미합니다. 다른 카메라를 사용하려면 숫자를 변경하세요.

# 서버 엔드포인트 URL 설정
server_url = "http://3.36.70.207:5000/upload"  # 서버 URL을 적절하게 변경하세요.

# 서버로 전송할 데이터 형식 설정 (이미지를 base64로 인코딩하여 전송)
headers = {"Content-Type": "application/json"}

# 이미지 크기와 압축 설정
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
JPEG_QUALITY = 80

# 카메라 해상도 설정
cap.set(3, IMAGE_WIDTH)
cap.set(4, IMAGE_HEIGHT)


# 이미지를 서버로 비동기로 전송하는 함수
async def send_image_to_server_async(image_base64):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json={"image": image_base64}, headers=headers) as response:
            if response.status == 200:
                print("이미지 전송 성공")

async def capture_and_send():
    i = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 이미지 크기 조정
        frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))

        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        image_base64 = base64.b64encode(buffer).decode()
        # print(image_base64)
        print(i,"success")
        i = i+1

        # 이미지를 서버로 비동기로 전송
        await send_image_to_server_async(image_base64)
        await asyncio.sleep(1 / 120)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()



# ----------------- 테스트2 --------------
@sio.on('camera_video')
def give_video(data):
    if data == "start":
        asyncio.run(capture_and_send())
    elif data == "end":
        # stop take image
        print("end")
        
        
        
        



if __name__ == '__main__' :
    gpio.setmode(gpio.BCM)
    sio.connect('http://3.36.70.207:5000')