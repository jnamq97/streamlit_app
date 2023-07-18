import cv2
import socket
import pickle
import struct
import time

# 서버 주소와 포트
server_address = ("server ip", "port")

# 웹캠 열기
cap = cv2.VideoCapture(0)

# 프레임 크기 지정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 가로
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 세로

# 소켓 생성 및 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

print("Connected !")
try:
    while True:
        # 프레임 읽기
        retval, frame = cap.read()
        retval, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

        pkl_frame = pickle.dumps(encoded_frame)

        print("Frame Sended ! : {} bytes".format(len(pkl_frame)))
        # time.sleep(1)
        error_code = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if error_code != 0:
            print("연결이 종료되었습니다.")
        else:
            client_socket.sendall(struct.pack("L", len(pkl_frame)) + pkl_frame)
        
        # # 프레임 디스플레이
        # cv2.imshow("Local Webcam", frame)
        # if cv2.waitKey(1) == ord("q"):
        #     break
except:
    # 메모리를 해제
    print("try except")
    cap.release()
    client_socket.close()