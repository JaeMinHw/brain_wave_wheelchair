from socket import *
import threading
import time
import json
import os
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import pymysql
from flask import Flask
from flask_cors import CORS
from flask import request, jsonify
import base64
import websockets
import cv2
import numpy as np
import asyncio
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials





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



# db연결
def dbconn(host,port,username,password,database) :
    try :
        conn = pymysql.connect(
            host=host,
            user=username,
            password=password,
            db=database,
            port=port)
        cursor = conn.cursor()

    except:
        print("RDS에 연결되지 않습니다")
    return conn,cursor


# 초기 화면
@app.route('/')
def hello():
    return "Hello World!"

# 아이디 체크
@app.route('/check/<string:checkid>')
def check(checkid):
    global host
    global port
    global username
    global database
    global password
    
    conn,cursor = dbconn(host,port,username,password,database)
    
    query = """select protect_regi,user_id from user where user_id = %s  """
    val = (checkid)
    cursor.execute(query,val)

    rows = cursor.fetchall()

    for row in rows:
        protect_regi = row[0]
        user_id = row[1]
        print(protect_regi, user_id)
        if protect_regi == 0:
            return "possible"

    
    return "fail"

# # 아이디 중복 확인
# @app.route('/check/<string:id>')
# def che(id) :
#     return dupliSign(id)

# 로그인 -- 아이디 비밀번호 확인
@app.route('/login/<string:id>/<string:pw>')
def Login(id,pw) :
    # 휠체어 사용자의 테이블에서 확인. 만약 사용자에서 있으면 user 반환
    # 만역 없으면 보호자에서 확인. 만약 보호자에서 있으면 protect 반환
    # 둘 다 없으면 fali
    
    global host
    global port
    global username
    global database
    global password
    
    conn,cursor = dbconn(host,port,username,password,database)
    
    query = """select * 
    from user
    where user_id = %s and user_pw = %s """
    
    val = (id,pw)
    
    cursor.execute(query,val)
    rows = cursor.fetchall()
    
    # 이미 id가 존재할 때
    if(len(rows) == 1) :
        conn.close()
        return "user"
        

    # user에서 아이디가 중복이 안될 때
    elif(len(rows) == 0) :
        query = """select * 
        from protect
        where pro_id = %s and pro_pw = %s """
        
        val = (id,pw)
        
        cursor.execute(query,val)
        rows = cursor.fetchall()
        if(len(rows) == 1):
            conn.close()
            return "pro"
    conn.close()
    return 'fail'

# 사용자 회원가입
@app.route('/signup/<string:id>/<string:pw>/<string:phone>')
def Signup(id,pw,phone) :
    # 아이디가 중복되면 실패
    # 중복되지 않게 
    
    # 가능
    if user_dupliSign("user",id) == "nonexist" :
        global host
        global port
        global username
        global database
        global password
    
        conn,cursor = dbconn(host,port,username,password,database)
        query = """insert into user(user_id, user_pw,user_phone)
                value(%s,%s,%s)"""
        val = (id,pw,phone)
        cursor.execute(query,val)
        conn.commit()
        conn.close()
        return "success"
    
    else :
        return "fail"
    



# 보호자 회원가입
@app.route('/prosignup/<string:wheelid>/<string:id>/<string:pw>/<string:phone>')
def ProSignup(wheelid,id,pw,phone) :
    
        # 가능
    if pro_dupliSign("protect",id) == "nonexist" :
        global host
        global port
        global username
        global database
        global password
    
        conn,cursor = dbconn(host,port,username,password,database)
        query = """insert into protect(pro_id, pro_pw,pro_phone,user_id)
                value(%s,%s,%s,%s)"""
        val = (id,pw,phone,wheelid)
        cursor.execute(query,val)
        conn.commit()
        conn.close()
        return "success"
    
    else :
        return "fail"
    
    
    
# 보호자 전화걸기
@app.route('/call/<string:id>')
def call_number(id):
    print(id, "전화번호 출력")
    global host
    global port
    global username
    global database
    global password
    conn,cursor = dbconn(host,port,username,password,database)
    query = """select user_phone
        from protect p, user u
        where p.pro_id = %s and p.user_id = u.user_id"""
        
    val = (id)
        
    cursor.execute(query,val)
    rows = cursor.fetchall()

    for row in rows:
        phone = row[0]

        print(phone)
        return phone
    return None



# 충격 감지 <사용자 아이디>
@app.route('/crash/<string:who>')
def crash(who):
    # 충격받은 사용자
    print("충격 감지")
    c = os.getcwd()
    print(c)
    if not firebase_admin._apps:
        cred = credentials.Certificate(c+"/brain-ewc-firebase-adminsdk-ulueg-8a2accc282.json")
        firebase_admin.initialize_app(cred)
    global host
    global port
    global username
    global database
    global password
    
    conn,cursor = dbconn(host,port,username,password,database)
    
    query = """select device_tok 
    from protect, protect_device
    where user_id = %s and protect.pro_id = protect_device.pro_id """
    
    val = (who)
    
    cursor.execute(query,val)
    rows = cursor.fetchall()
    
    for row in rows:
       
        registration_token = row[0]
        print(registration_token)
        
    
    message = messaging.Message(
        notification=messaging.Notification(
            title="충격이 감지되었습니다.",
            body=" 사용자의 휠체어에 충격이 감지되었습니다.\n확인해주세요",
        ),
        token=registration_token,
    )

    response = messaging.send(message)
    print('Successfully sent message:', response)
    conn.close()
    return "success"
    
    
@app.route('/token/<string:who>/<string:tok>')
def tok(who,tok):
    global host
    global port
    global username
    global database
    global password

    conn,cursor = dbconn(host,port,username,password,database)
    query1 = """delete from protect_device where pro_id = %s """
    val = (who)
    cursor.execute(query1,val)
    
    query = """insert into protect_device(pro_id, device_tok)
            value(%s,%s)"""
    val = (who,tok)
    cursor.execute(query,val)
    conn.commit()
    conn.close()
    return "success"



# 사용자 위치 저장
@app.route('/place/<string:user_id>/<string:latitude>/<string:longitude>')
def place(user_id,latitude,longitude):
    print("사용자 위치 저장")
    global host
    global port
    global username
    global database
    global password

    conn,cursor = dbconn(host,port,username,password,database)
    
    query1 = """delete from user_place where user_id = %s"""
    val1 = (user_id)
    cursor.execute(query1,val1)
    conn.commit()
    conn.close()
    query = """insert into user_place(user_id,latitude,longitude) value(%s,%s,%s)"""
    conn,cursor = dbconn(host,port,username,password,database)
    val = (user_id,latitude,longitude)
    cursor.execute(query,val)
    conn.commit()
    conn.close()
    return "success"
    

    
    
    
# 보호자에게 사용자 위치 반환
@app.route('/place/pro/<string:pro_id>')
def place1(pro_id):
    print("보호자에게 전송")
    global host
    global port
    global username
    global database
    global password

    conn,cursor = dbconn(host,port,username,password,database)
    query = """select latitude, longitude from protect,user_place where protect.pro_id = %s and protect.user_id = user_place.user_id """
    val = (pro_id)
    cursor.execute(query,val)
    
    rows = cursor.fetchall()
    data = {}

    for row in rows:
        data['latitude'] = row[0]
        data['longitude'] = row[1]
    
    
    print(data)
        
        
    conn.close()
    return data
    
    
    
@app.route('/status/<string:sen>')
def sensor(sen):
    print(sen)
    socketio.emit("sensor",sen)
    
    
# ----------------- define -------------------- 

# 보호자 회원가입 할 때 휠체어 사용자의 보호자 유무 확인
def duplipro(id) :
    return 'success'
    

# 회원가입 시 아이디 중복 확인 함수
def user_dupliSign(who,id):
    global host
    global port
    global username
    global database
    global password
    
    conn,cursor = dbconn(host,port,username,password,database)
    
    # query_user = """select count(*) from test where  ID = %s """,id
    # query_user = """select * from user where ID = %s""",id
    query_user = """select * from user where user_id = %s """

    val = (id)
    cursor.execute(query_user,val)
    rows = cursor.fetchall()
    print(len(rows))
    
    # 이미 id가 존재할 때
    if(len(rows) == 1) :
        conn.close()
        return "exist"
        

    # user에서 아이디가 중복이 안될 때
    elif(len(rows) == 0) :
        conn.close()
        return "nonexist"
        # conn1,cursor1 = dbconn(host,port,username,password,database)
        # query_pro = """select count(*) from protect where %s""",id
        # cursor1.execute(query_pro)
        # rows1 = cursor1.fetchall()
        
        

    # conn1,cursor1 = dbconn(host,port,username,password,database)
    # query_pro = """select count(*) from protect where %s""",id
    # cursor1.execute(query_pro)
    # rows1 = cursor1.fetchall()
    

    conn.close()
    return 'fali'


# 회원가입 시 아이디 중복 확인 함수
def pro_dupliSign(who,id):
    global host
    global port
    global username
    global database
    global password
    
    conn,cursor = dbconn(host,port,username,password,database)
    
    # query_user = """select count(*) from test where  ID = %s """,id
    # query_user = """select * from user where ID = %s""",id
    query_user = """select * from protect where user_id = %s """

    val = (id)
    cursor.execute(query_user,val)
    rows = cursor.fetchall()
    print(len(rows))
    
    # 이미 id가 존재할 때
    if(len(rows) == 1) :
        conn.close()
        return "exist"
        

    # user에서 아이디가 중복이 안될 때
    elif(len(rows) == 0) :
        conn.close()
        return "nonexist"
        # conn1,cursor1 = dbconn(host,port,username,password,database)
        # query_pro = """select count(*) from protect where %s""",id
        # cursor1.execute(query_pro)
        # rows1 = cursor1.fetchall()

        
        

    # conn1,cursor1 = dbconn(host,port,username,password,database)
    # query_pro = """select count(*) from protect where %s""",id
    # cursor1.execute(query_pro)
    # rows1 = cursor1.fetchall()
    

    conn.close()
    return 'fali'







# ----------------- socketio -------------------- 

# 휠체어 제어를 위한 rest
@app.route('/brain_wave/<string:value>')
def brain_wave(value) :
    socketio.emit("order",value)
    return "success" + value


@socketio.on('connect')
def connect() :
    socketio.emit("response","너 연결")

@socketio.on("request1")
def request1(message) :
    print("message : " + message )
    socketio.emit("order",message)
    
    
@socketio.on('message')
def message(message) :
    print(message)
    
    
@socketio.on('start_video')
def video_conn(data):
    # 라즈베리 파이에게 카메라 달라고 하기
    socketio.emit('camera_video',"start")
    
@socketio.on('end_video')
def video_conn(data):
    # 라즈베리 파이에게 카메라 달라고 하기
    socketio.emit('camera_video',"end")
    
    

# 이미지 데이터를 읽어올 함수
async def read_image_data():
    # 이미지를 캡쳐하고 이미지 파일에서 읽어옴 (captured_image2.jpg는 최종으로 업데이트된 이미지 파일)
    # 이 부분을 실제 이미지 캡쳐 코드로 대체해야 합니다.
    with open("captured_image2.jpg", "rb") as image_file:
        return image_file.read()

# WebSocket 서버 설정
async def image_server(websocket, path):
    try:
        while True:
            # 이미지 데이터 읽기
            image_data = await read_image_data()

            # 이미지를 base64로 인코딩
            image_base64 = base64.b64encode(image_data).decode()

            # 클라이언트로 이미지 전송
            await websocket.send(image_base64)

            # 60프레임 주기로 이미지를 전송하기 위해 대기 (약 16ms 대기)
            await asyncio.sleep(1 / 120)
    except websockets.exceptions.ConnectionClosedOK:
        pass

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json

        if 'image' in data:
            # base64로 인코딩된 이미지를 디코딩하여 이미지 데이터로 변환
            image_base64 = data['image']
            image_data = base64.b64decode(image_base64)

            # 이미지 데이터를 numpy 배열로 변환
            image_np = np.frombuffer(image_data, dtype=np.uint8)
            
            # OpenCV를 사용하여 이미지로 변환
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            # 이미지를 디스크에 저장 (예시: "captured_image2.jpg"로 저장)
            cv2.imwrite("captured_image2.jpg", image)

            return jsonify({"message": "이미지 업로드 및 저장 성공"}), 200
        else:
            return jsonify({"error": "이미지 데이터가 전송되지 않았습니다."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_websocket_server():
    asyncio.set_event_loop(asyncio.new_event_loop())  # 이벤트 루프 생성
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(image_server, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

@app.route('/test/<string:value>')
def test(value):
    return value



if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    websocket_thread = threading.Thread(target=run_websocket_server)
    websocket_thread.start()
    socketio.run(app, host='0.0.0.0',port = 5000)
    
