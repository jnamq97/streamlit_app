from streamlit_webrtc import webrtc_streamer
import os
import cv2
from matplotlib import pyplot as plt
from twilio.rest import Client
import streamlit as st
from ultralytics import YOLO
import numpy as np
# for audio
import av
from pydub import AudioSegment
from pydub.playback import play
import threading
import base64
import time

def generate_label_colors(classes=26):
    return np.random.uniform(0, 255, size=(classes, 3))


model = YOLO("/app/streamlit_app/weights/yolov8n_100epoch_.pt")
COLORS = generate_label_colors()
event_triggered = True
box_len = 0
lock = threading.Lock()
img_container = {"img": None}

def change_box_len():
    global box_len
    box_len += 1
    

def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    preds = model(image)

    boxes = preds[0].boxes.boxes
    classes = preds[0].names

    with lock:
        img_container["img"] = image
        
    for xmin, ymin, xmax, ymax, score, label in boxes:
        xmin, ymin, xmax, ymax = map(int, [xmin, ymin, xmax, ymax])
        label_name = classes[int(label.item())]
        color = COLORS[int(label.item())]
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(
            image,
            label_name,
            (xmin, ymin - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2,
        )

    # if len(boxes) > 1:
    #     # st.audio(recorded_audio_file)
    #     change_box_len()

    #     # 클라이언트 측에서 오디오 재생
    #     play(AudioSegment.from_file(recorded_audio_file))

    return av.VideoFrame.from_ndarray(image, format="bgr24")


# def play_recorded_audio(recorded_audio_file):
#     audio = AudioSegment.from_file(recorded_audio_file)
#     play(audio)

def autoplay_audio(file_path: str):
    audio_place = st.empty()
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        audio_place.markdown(
            md,
            unsafe_allow_html=True,
        )
    time.sleep(2)
    audio_place.empty()

def webrtc_init():
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    self_ctx = webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        async_processing=True,
        key="apas",
    )


    temp = 0
    text_place = st.empty()
    audio_place = st.empty()
    recorded_audio_file = "/app/streamlit_app/webcam/webrtc/output.mp3"
    audio_file = open(recorded_audio_file,'rb')
    audio_bytes = audio_file.read()

    while self_ctx.state.playing:
        with lock:
            image = img_container["img"]
            temp += 1
        text_place.text(temp)
        if temp % 10 == 0:
            autoplay_audio(recorded_audio_file)


