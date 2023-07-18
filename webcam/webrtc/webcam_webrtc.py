from streamlit_webrtc import webrtc_streamer
import os
import cv2
from matplotlib import pyplot as plt
from twilio.rest import Client
import streamlit as st
import av
from ultralytics import YOLO


model = YOLO("yolov8n.pt")


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    h, w = image.shape[:2]
    preds = model(image)

    boxes = preds[0].boxes.boxes
    classes = preds[0].names

    for xmin, ymin, xmax, ymax, score, label in boxes:
        label = classes[int(label.item())]
        cv2.rectangle(
            image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (255, 0, 0), 2
        )
        cv2.putText(
            image,
            label,
            (xmin, ymin - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
        )

    return av.VideoFrame.from_ndarray(image, format="bgr24")


def webrtc_init():
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_callback,
        async_processing=True,
        key="apas",
    )
