from streamlit_webrtc import webrtc_streamer
import os
import cv2
from matplotlib import pyplot as plt
from twilio.rest import Client
import streamlit as st
import av
from ultralytics import YOLO
import numpy as np
import threading
from warning_system.warning_system import warning_state_Algorithm


# @st.cache_resource  # type: ignore
def generate_label_colors(classes=26):
    return np.random.uniform(0, 255, size=(classes, 3))


model = YOLO("/app/streamlit_app/weights/yolov8n_100epoch_.pt")
COLORS = generate_label_colors()

lock = threading.Lock()
warning_message = {"warning": None}


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    h, w = image[0].orig_shape
    preds = model(image)

    boxes = preds[0].boxes.boxes
    classes = preds[0].names

    warning = 0
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
        warning = max(
            warning_state_Algorithm(xmin, ymin, xmax, ymax, int(label.item()), w, h),
            warning,
        )

    with lock:
        warning_message["warning"] = warning

    return av.VideoFrame.from_ndarray(image, format="bgr24")


def webrtc_init():
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    ctx = webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        async_processing=True,
        key="apas",
    )
    while ctx.state.playing:
        with lock:
            warning = warning_message["warning"]
        if warning != 3:
            continue
        st.text("warning red !!!")
