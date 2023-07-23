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
from warning_system.warning_system import warning_state_Algorithm
import queue


def generate_label_colors(classes=29):
    return np.random.uniform(0, 255, size=(classes, 3))


COLORS = generate_label_colors()
event_triggered = True
# img_container = {"img": None}
obj_contatiner = {"obj": None}
result_queue: "queue.Queue[List[Detection]]" = queue.Queue()
frame_queue = queue.Queue()


def create_video_frame_callback():
    frame_count = 0

    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        nonlocal frame_count

        frame_count += 1
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
            # danger.append(label_name)
            danger.append(
                (warning_state_Algorithm(xmin, ymin, xmax, ymax, label_name, h, w))
            )
        if frame_count % 20 == 0:
            result_queue.put(danger)
        frame_queue.put(frame_count)

        return av.VideoFrame.from_ndarray(image, format="bgr24")

    return video_frame_callback


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
    time.sleep(1.5)
    audio_place.empty()


def webrtc_init():
    global model

    model = YOLO("/app/streamlit_app/weights/yolov8n_jp_real.pt")
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    video_frame_cb = create_video_frame_callback()

    ctx = webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=video_frame_cb,
        async_processing=True,
        key="apas",
    )

    recorded_audio_file = "/app/streamlit_app/webcam/webrtc/output.mp3"
    text_place = st.empty()
    danger_place = st.empty()
    while ctx.state.playing:
        frame_num = frame_queue.get()
        if frame_num % 30 == 0:  # for every 30 frames
            result = result_queue.get()
            text_place.text(frame_num)
            if len(result) != 0:
                autoplay_audio(recorded_audio_file)
                # audio_place = st.empty()
                # with open(recorded_audio_file, "rb") as f:
                #     data = f.read()
                #     b64 = base64.b64encode(data).decode()
                #     md = f"""
                #         <audio controls autoplay="true">
                #         <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                #         </audio>
                #         """
                #     audio_place.markdown(
                #         md,
                #         unsafe_allow_html=True,
                #     )
                # time.sleep(1)
                # audio_place.empty()

    # if len(result):
    #     text_place.text(result)
    # audio_place = st.empty()
    # with open(recorded_audio_file, "rb") as f:
    #     data = f.read()
    #     b64 = base64.b64encode(data).decode()
    #     md = f"""
    #         <audio controls autoplay="true">
    #         <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    #         </audio>
    #         """
    #     audio_place.markdown(
    #         md,
    #         unsafe_allow_html=True,
    #     )
    # time.sleep(2)
    # audio_place.empty()
    # else:
    #     text_place.text("no detection !")
    # else:
    #     text_place.text("no results")

    # if len(result) != 0:
    #     autoplay_audio(recorded_audio_file)
