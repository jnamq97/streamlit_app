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

# from warning_system.warning_system import warning_state_Algorithm
import queue


def generate_label_colors(classes=80):
    return np.random.uniform(0, 255, size=(classes, 3))


COLORS = generate_label_colors()
lock = threading.Lock()
# img_container = {"img": None}
obj_contatiner = {"obj": None}
result_queue: "queue.Queue[List[Detection]]" = queue.Queue()
frame_queue: "queue.Queue[List[Detection]]" = queue.Queue()
# result_queue_class: "queue.Queue[List[Detection]]" = queue.Queue()


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    preds = model(image)
    h, w = preds[0].orig_shape

    boxes = preds[0].boxes.data
    classes = preds[0].names
    danger = []

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
        danger.append(label_name)
        # result_queue_class.put(int(label.item()))
    result_queue.put(danger)
    frame_queue.put(max(0, len(danger)))
    danger = []

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
    global model

    model = YOLO("/app/Desktop/streamlit_app/weights/yolov8n.pt")

    # # for server
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    # # for local
    # account_sid = "ACeb8a5d5ee729398212c989f889ceb1f7"
    # auth_token = "33e5593eb4d5253c797afd9a35ecca71"
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    ctx = webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        async_processing=True,
        key="apas",
    )

    text_place = st.empty()
    recorded_audio_file = "/app/streamlit_app/webcam/webrtc/output.mp3"

    dangers = []
    frame_count = 0
    while ctx.state.playing:
        is_frame = frame_queue.get()
        dangers = result_queue.get()
        # st.text(f"outside dangers : {dangers}")
        # st.text(f"outside is_frame : {is_frame}")
        # st.text(f"frame count : {frame_count}")
        if is_frame:
            frame_count += 1
            if frame_count % 20 == 0:
                if dangers is None:
                    continue
                elif len(dangers) > 0:
                    text_place.text(f"warning : {dangers}")
                    autoplay_audio(recorded_audio_file)
            else:
                continue

        # result_class = result_queue_class.get()
        # st.text(result_class)
