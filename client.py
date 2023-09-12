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

import RPi.GPIO as gpio
import time

import cv2
import asyncio
import aiohttp
import base64

# 로컬 카메라 캡처 객체 생성
cap = cv2.VideoCapture(0)  # 0은 기본 카메라를 의미합니다. 다른 카메라를 사용하려면 숫자를 변경하세요.

# 서버 엔드포인트 URL 설정
server_url = "http://3.36.70.207:5000/upload"  # 서버 URL을 적절하게 변경하세요.

# 서버로 전송할 데이터 형식 설정 (이미지를 base64로 인코딩하여 전송)
headers = {"Content-Type": "application/json"}

# 이미지 크기와 압축 설정
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240
JPEG_QUALITY = 50

# 카메라 해상도 설정
cap.set(3, IMAGE_WIDTH)
cap.set(4, IMAGE_HEIGHT)

port = "/dev/ttyACM1"
ard = serial.Serial(port,9600)


 
TRIGER = 24
ECHO = 23

TRIGER2 = 27
ECHO2 = 22

TRIGER3 = 6
ECHO3 = 5

TRIGER4 = 25
ECHO4 = 17  

 
gpio.setmode(gpio.BCM)
gpio.setup(TRIGER, gpio.OUT)
gpio.setup(ECHO, gpio.IN)


sio = socketio.Client()


thread1 = None
thread2 = None
thread3 = None
thread4 = None


# after distance detect, if distance is too close, s = '7' ard.write(s.encode()) 



@sio.event
def connect() :
    print('Connect to server')
    
    

@sio.on('order')
def order(data):
    print('Received response:',data)
    move(data)
    x = Cal_distance()
    y = Cal_distance()
    z = Cal_distance()
    k = Cal_distance()
    thread1 = threading.Thread(target=x.cal_distance,args = ("t1",TRIGER,ECHO))
    thread2 = threading.Thread(target=y.cal_distance,args=("t2",TRIGER2,ECHO2))
    thread3 = threading.Thread(target=z.cal_distance,args = ("t3",TRIGER3,ECHO3))
    thread4 = threading.Thread(target=k.cal_distance,args = ("t4",TRIGER4,ECHO4))


    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()



class Cal_distance :
    def cal_distance(self,name,TRIGER,ECHO) :

 
        gpio.setmode(gpio.BCM)
        gpio.setup(TRIGER, gpio.OUT)
        gpio.setup(ECHO, gpio.IN)
        
        #period = endTime - startTime에서 startTime값이 null인 경우 발생->초기화
        startTime = time.time()  
        
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
        
                print( "Dist1", dist1, "cm", ", Dist2", dist2, "cm")
                
                if dist1 < 10 and dist2 < 10:
                    move("stop")
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
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()

@sio.on('response')
def response(data):
    print(data)
    
    
    
    
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
        print(image_base64)
        print(i,"success")
        i = i+1

        # 이미지를 서버로 비동기로 전송
        await send_image_to_server_async(image_base64)
        await asyncio.sleep(1 / 120)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()





# # ----------------- 테스트2 --------------
# @sio.on('camera_video')
# def give_video(data):
#     if data == "start":
#         # take image, give to server
#         print("start")
#         good = """sudo mjpg_streamer -i 'input_uvc.so' -o 'output_http.so -w /usr/local/share/mjpg-streamer/www -p 9090'&"""
#         os.system(good)
#         time.sleep(2)
        
#         capt = asyncio.get_event_loop().run_until_complete(main())

#     elif data == "end":
#         # stop take image
#         print("end")
#         capt.cancel()
        
        
        
# async def capture_and_encode_image():
#     # 이미지 캡처
#     capture = cv2.VideoCapture("http://127.0.0.1:9090/?action=stream")
#     ret, frame = capture.read()
#     frame = cv2.resize(frame, dsize=(int(320*1.8),int(240*1.8)), interpolation = cv2.INTER_AREA)

#     capture.release()
#     # 이미지 인코딩
#     _, encoded_image = cv2.imencode('.jpg', frame)
#     image_base64 = base64.b64encode(encoded_image).decode('utf-8')

#     return image_base64


# async def send_image_to_server(image_base64):
#     print(image_base64)
#     socketio.emit('upload',image_base64)





# async def main():
#     while True:
#         try:
#             # 이미지 캡처 및 인코딩 비동기로 처리
#             image_base64 = await capture_and_encode_image()

#             # 이미지 서버로 전송 비동기로 처리
#             await send_image_to_server(image_base64)
#             # 일정 시간 간격으로 반복
#             await asyncio.sleep(1/60)


#         except Exception as e:
#             print("에러 발생:", str(e))



# # ----------------- 테스트 2 end --------------






# ----------------- 테스트1 --------------
# @sio.on('camera_video')
# def give_video(data):
#     if data == "start":
#         # take image, give to server
#         print("start")
#         good = """sudo mjpg_streamer -i 'input_uvc.so' -o 'output_http.so -w /usr/local/share/mjpg-streamer/www -p 9090'&"""
#         os.system(good)
#         time.sleep(2)
        
#         capt = asyncio.get_event_loop().run_until_complete(main())

#     elif data == "end":
#         # stop take image
#         print("end")
#         capt.cancle()


    
# async def capture_and_encode_image():
#     # 이미지 캡처
#     capture = cv2.VideoCapture("http://127.0.0.1:9090/?action=stream")
#     ret, frame = capture.read()
#     frame = cv2.resize(frame, dsize=(int(320*1.8),int(240*1.8)), interpolation = cv2.INTER_AREA)

#     capture.release()
#     # 이미지 인코딩
#     _, encoded_image = cv2.imencode('.jpg', frame)
#     image_base64 = base64.b64encode(encoded_image).decode('utf-8')

#     return image_base64

# async def send_image_to_server(image_base64):
#     url = "http://43.200.191.244:5000/upload"  # 실제 서버 주소와 포트를 입력하세요
#     payload = {"image": image_base64}
#     headers = {"Content-Type": "application/json"}

#     response = await asyncio.get_event_loop().run_in_executor(
#         None, lambda: requests.post(url, json=payload, headers=headers)
#     )
#     return response

# async def main():
#     while True:
#         try:
#             # 이미지 캡처 및 인코딩 비동기로 처리
#             image_base64 = await capture_and_encode_image()

#             # 이미지 서버로 전송 비동기로 처리
#             response = await send_image_to_server(image_base64)

#             if response.status_code == 200:
#                 print("이미지 전송 성공")
#             else:
#                 print("이미지 전송 실패")

#         except Exception as e:
#             print("에러 발생:", str(e))

#         # 일정 시간 간격으로 반복
#         await asyncio.sleep(1/60)


if __name__ == '__main__' :
    sio.connect('http://3.36.70.207:5000')
    asyncio.run(capture_and_send())
    