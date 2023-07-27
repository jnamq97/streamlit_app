import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import cv2
from webcam.socket.webcam_server import main as webcam_main
from webcam.webrtc.webcam_webrtc import create_video_frame_callback, webrtc_init
from streamlit_webrtc import webrtc_streamer
import sys
from streamlit_option_menu import option_menu

# from yolo_tracking.examples.track import *


def show_app(image_placeholder, img):
    image_placeholder.image(img)


def main():
    # os.environ["yolo_tracking"] = st.secrets["PATH"]

    # st.subheader("CV-10 : Bro3Sis1 Team")
    first_call = True

    with st.sidebar:
        mode = option_menu(
            "APAS",
            ["Online", "Offline", "How to Use"],
            icons=["house", "bi bi-robot", "gear"],
            menu_icon="cast",
            default_index=0,
        )
    header_place = st.empty()
    if mode == "Online":
        st.subheader("APAS (Advanced Pedestrian Assistance System)")
        st.header("Online Inference Mode")
        with st.spinner("webcam"):
            # if webcam_button:
            webrtc_init()

    elif mode == "Offline":
        st.subheader("APAS (Advanced Pedestrian Assistance System)")
        st.header("Offline Inference Mode")
        data_type = st.selectbox("Please select data type !", ("Image", "Video"))
        # upload data
        if data_type == "Image":
            st.info("Input Image File(.png or .jpg) to Inference")
            uploaded_file = st.file_uploader(
                "Input Image",
                accept_multiple_files=True,
                type=["png", "jpg"],
                label_visibility="collapsed",
            )
        elif data_type == "Video":
            st.info("Input Video File(.avi or .mp4) to Inference")
            uploaded_file = st.file_uploader(
                "Input Video",
                accept_multiple_files=True,
                type=["avi", "mp4"],
                label_visibility="collapsed",
            )

        button = st.button("Start Inference")

        # with st.spinner("Inference In Progress"):
        #     if button:
        #         button = False
        #         # track.py
        #         opt = parse_opt()

        #         if uploaded_file:
        #             for file in uploaded_file:
        #                 # save file to tempDB
        #                 saved_dir = os.path.join(
        #                     "/mount/src/streamlit_app/yolo_tracking/examples/tempDB",
        #                     file.name,
        #                 )
        #                 with open(saved_dir, "wb") as f:
        #                     f.write(file.getbuffer())

        #                 st.success("File Uploaded !")

        #                 opt.source = saved_dir
        #                 opt.streamlit = True
        #                 opt.show = True

        #                 result = run(vars(opt))
        #                 st.success("Inference Complete !")

        #         else:
        #             st.error("Please Input Necessary Data !")
    elif mode == "How to Use":
        st.subheader("APAS를 소개합니다 ❗️")
        st.write(
            "APAS(Advanced Pedestrian Assistance System)는 시각 장애인을 대상으로 개발된 보행 보조 시스템입니다.\n"
        )
        st.subheader("1️⃣ Online mode란?")
        st.write("실시간 보행 보조를 실행하는 모드입니다. 사용자의 카메라 영상을 기반으로 위험을 감지해 음성으로 경고를 줍니다.\n")
        st.write("1. select device를 통해 연결된 카메라를 선택해주세요.\n")
        st.write("2. start 버튼을 눌러 실시간 보행 보조를 실행합니다.\n")
        st.subheader("2️⃣ Offline mode란?")
        st.write("보행 상황 이미지나 영상을 업로드하여 APAS의 성능을 시험해보는 모드입니다.\n")
        st.write("1. data type을 image/video 중에 선택해주세요.\n")
        st.write("2. browse file을 누르거나 드래그를 통해 테스트할 파일을 올려주세요.\n")
        st.write("3. start infernce를 눌러 결과를 확인해보세요.\n")
        st.write("\nmade by : Boostcamp AITech 5기 CV-10조 Bro3sis1 Team")


if __name__ == "__main__":
    main()
