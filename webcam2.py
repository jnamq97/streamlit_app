import cv2
import socket
import numpy as np
import streamlit as st
import struct
import pickle


def main(first_call):
    if first_call:
        # 서버 주소와 포트
        server_address = ("0.0.0.0", 30010)

        # 소켓 생성 및 바인딩
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 소켓 옵션 설정
        server_socket.bind(server_address)

        # 클라이언트 연결 대기
        server_socket.listen(1)
        print("Waiting for client connection...")

        # 클라이언트 소켓 수락
        client_socket, client_address = server_socket.accept()
        print("Client connected:", client_address)

    # 비디오 스트림 수신 및 디스플레이
    image_placeholder = st.empty()
    data_buffer = b""
    data_size = struct.calcsize("L")
    while True:
        # 설정한 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
        while len(data_buffer) < data_size:
            # 데이터 수신
            data_buffer += client_socket.recv(4096)

        # 버퍼의 저장된 데이터 분할
        packed_data_size = data_buffer[:data_size]
        data_buffer = data_buffer[data_size:]
        frame_size = struct.unpack("L", packed_data_size)[0]

        # 프레임 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
        while len(data_buffer) < frame_size:
            # 데이터 수신
            data_buffer += client_socket.recv(4096)

        # 프레임 데이터 분할
        frame_data = data_buffer[:frame_size]
        data_buffer = data_buffer[frame_size:]

        frame = pickle.loads(frame_data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        print("Frame received ! : {} bytes".format(frame_size))

        # yolo inference 통과
        # 매번 model 불러오면 답없음

        from app import show_app

        show_app(image_placeholder, frame)

        # 프레임 디스플레이
        # cv2.imshow("Received Frame", frame)
        # if cv2.waitKey(1) == ord("q")
        #     break

    # 리소스 해제
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    server_socket.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
