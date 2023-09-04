from socket import *
import threading
import time
import json
import os
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import pymysql
from flask import request
from flask import Flask
from flask_cors import CORS
# from firebase_admin import messaging
# import firebase_admin
# from firebase_admin import credentials





from flask_sslify import SSLify
app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

host = "gradu-server.czrwdvnwjxlw.ap-northeast-2.rds.amazonaws.com"
port = 3306
username = "root"
database = "ewc"
password = "woals9127!"

data1 = None



@socketio.on('start_video')
def video_conn(data):
    # 라즈베리 파이에게 카메라 달라고 하기
    socketio.emit('camera_video',"start")
    print("start")
    
    
    
# 라즈베리파이에서 서버로 이미지 전송
@socketio.on('upload')
def rasp_to_server(data):
    global data1
    data1 = data
    print("Test")
    print(data)
    socketio.emit('stream',data1,broadcast=True)
    


    
# 라즈베리파이에서 이미지 주는 경로
@app.route('/upload', methods=['POST'])
def handle_upload():
    image = request.json['image']
    # 이미지 처리 로직을 수행
    # 안드로이드가 받을 수 있게
    socketio.emit('stream',image,broadcast = True)
    print("test")
    return 200


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    socketio.run(app, host='0.0.0.0',port = 5001)
