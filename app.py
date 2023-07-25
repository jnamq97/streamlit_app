import streamlit as st
import pandas as pd
import numpy as np
import time
from yolo_tracking.examples.track import *
import os
import cv2
from webcam.socket.webcam_server import main as webcam_main
from webcam.webrtc.webcam_webrtc import create_video_frame_callback, webrtc_init
from streamlit_webrtc import webrtc_streamer


def show_app(image_placeholder, img):
    image_placeholder.image(img)


def main():
    os.environ["yolo_tracking"] = st.secrets["PATH"]

    st.title("APAS (Advanced Pedestrian Assistance System)")
    st.subheader("CV-10 : Bro3Sis1 Team")
    first_call = True

    mode = st.sidebar.selectbox(
        "Please selecet Inference Mode !", ("Online", "Offline")
    )

    if mode == "Online":
        st.header("Online Inference Mode")
        with st.spinner("webcam"):
            # if webcam_button:
            webrtc_init()

    elif mode == "Offline":
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

        with st.spinner("Inference In Progress"):
            if button:
                button = False
                # track.py
                opt = parse_opt()

                if uploaded_file:
                    for file in uploaded_file:
                        # save file to tempDB
                        saved_dir = os.path.join(
                            "/app/streamlit_app/yolo_tracking/examples/tempDB",
                            file.name,
                        )
                        with open(saved_dir, "wb") as f:
                            f.write(file.getbuffer())

                        st.success("File Uploaded !")

                        opt.source = saved_dir
                        opt.streamlit = True
                        opt.show = True

                        result = run(vars(opt))
                        st.success("Inference Complete !")

                else:
                    st.error("Please Input Necessary Data !")


if __name__ == "__main__":
    main()
