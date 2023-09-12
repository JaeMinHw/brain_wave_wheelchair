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

if __name__ == "__main__":
    asyncio.run(capture_and_send())