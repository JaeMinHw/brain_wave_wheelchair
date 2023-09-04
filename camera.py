import cv2
import os, sys
import time
import base64
import websockets
import asyncio
from servomoter import servo
import numpy as np
from DHT_sensor import degree
from ast import literal_eval

good = """sudo mjpg_streamer -i 'input_uvc.so' -o 'output_http.so -w /usr/local/share/mjpg-streamer/www -p 9090'&"""

os.system(good)

time.sleep(2)
       
async def start():
    uri = "ws://15.165.96.230:50634"
    async with websockets.connect(uri, ping_interval=None) as websocket:
        Data = {'kind': 0, 'roomNumber' : "1234"}
        await websocket.send(str(Data))
        send_t = asyncio.create_task(sendImg(websocket))
        recvT = asyncio.create_task(recvCom(websocket))
        await recvT
        await send_t

async def recvCom(websocket):
    s = servo()
    while(1):
        get = await websocket.recv()
        get = literal_eval(get)
        if(get["command"]=="feed"):
            s.WaterOpen()
        else:
            s.FeedOpen()
           

async def sendImg(websocket):
    d = degree()
    capture = cv2.VideoCapture("http://127.0.0.1:9090/?action=stream")
    while(capture.isOpened()):
        ret, frame = capture.read()
        frame = cv2.resize(frame, dsize=(int(320*1.8),int(240*1.8)), interpolation = cv2.INTER_AREA)
        frame = cv2.putText(frame, "Degree : "+str(d.getDegree()), (0,50), cv2.FONT_ITALIC, 1, (255, 255, 255))
        frame = cv2.putText(frame, "Humidity : "+str(d.getHumidity()), (0,100), cv2.FONT_ITALIC, 1, (255, 255, 255))
       
        img = cv2.imencode('.jpg',frame)
       
        await websocket.send(base64.b64encode(img[1]).decode('utf-8'))
        await asyncio.sleep(1/60)
    capture.release()

asyncio.get_event_loop().run_until_complete(start())