# # 라즈베리 파이에 넣고 아두이노 제어하는 코드 추가해서 실행해보기

# import socketio

# sio = socketio.Client()

# @sio.event
# def connect():
#     print('Connected to server')

# @sio.on('order')
# def handle_response(data):
#     print('Received response:', data)
#     if data == 'go' :
#         ard.write("1")
#         # 아두이노 제어하기
    
# @sio.on('response')
# def response(message) :
#     print(message)

# if __name__ == '__main__':
#     sio.connect('http://127.0.0.1:5000')
#     # while True:
#     #     message = input('Enter a message (or "exit" to quit): ')
#     #     if message == 'exit':
#     #         break
#     #     sio.emit('message', message)
#     # sio.disconnect()





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