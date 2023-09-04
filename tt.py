import asyncio
import websockets
import threading
from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np

app = Flask(__name__)

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

if __name__ == '__main__':
    websocket_thread = threading.Thread(target=run_websocket_server)
    websocket_thread.start()

    app.run(host='0.0.0.0', port=5000)