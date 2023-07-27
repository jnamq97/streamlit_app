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
WARNING_LEVELS = {
    "1": (1, "right"),
    "2": (1, "left"),
    "3": (1, "center"),
    "4": (2, "right"),
    "5": (2, "left"),
    "6": (2, "center"),
    "7": (3, "center"),
}
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
            if frame_count % 50 == 0:
                # danger.append(label_name)
                danger.append(
                    (warning_state_Algorithm(xmin, ymin, xmax, ymax, label_name, h, w))
                )
        if frame_count % 50 == 0:
            result_queue.put(danger)
        frame_queue.put(frame_count)

        return av.VideoFrame.from_ndarray(image, format="bgr24")

    return video_frame_callback


def autoplay_audio(file_path: str, playback_rate=2.0):
    audio_place = st.empty()
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true" id="audio_element">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            <script>
                var audioElement = document.getElementById("audio_element");
                audioElement.playbackRate = {playback_rate};
            </script>
            """
        audio_place.markdown(
            md,
            unsafe_allow_html=True,
        )
    time.sleep(1.5)
    audio_place.empty()


def custom_audio_frame_callback(audio_frame: av.AudioFrame) -> av.AudioFrame:
    # Read the desired MP3 file
    mp3_file_path = "/mount/src/streamlit_app/webcam/webrtc/output.mp3"
    audio = AudioSegment.from_file(mp3_file_path)

    # Convert the audio to bytes
    audio_bytes = audio.raw_data

    # Set the audio_frame's buffer to the custom audio bytes
    audio_frame.buffer = audio_bytes

    return audio_frame


def webrtc_init():
    global model

    model = YOLO("/mount/src/streamlit_app/weights/yolov8n_jp_real.pt")
    os.environ["TWILIO_ACCOUNT_SID"] = st.secrets["TWILIO_ACCOUNT_SID"]
    os.environ["TWILIO_AUTH_TOKEN"] = st.secrets["TWILIO_AUTH_TOKEN"]

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    video_frame_cb = create_video_frame_callback()

    ctx = webrtc_streamer(
        rtc_configuration={"iceServers": token.ice_servers},
        media_stream_constraints={"video": True, "audio": True},
        video_frame_callback=video_frame_cb,
        audio_frame_callback=custom_audio_frame_callback,
        async_processing=True,
        key="apas",
    )

    # recorded_audio_file = "/app/streamlit_app/webcam/webrtc/output.mp3"
    # recorded_audio_files = {} ## dictionary로 파일 경로들 저장하거나 경로를 조합해야할듯.
    text_place = st.empty()
    danger_place = st.empty()
    while ctx.state.playing:
        frame_num = frame_queue.get()
        if frame_num % 50 == 0:  # for every 50 frames
            result = result_queue.get()

            if len(result) != 0:
                result.sort(key=lambda x: x[1], reverse=True)
                danger_class, danger_level = result[0]
                if danger_level != 0:  # except safe
                    text_place.warning("주의하세요 !")
                    lv, dir = WARNING_LEVELS[str(danger_level)]
                    audio_file_path = f"/mount/src/streamlit_app/webcam/webrtc/tts/{danger_class}_{lv}_{dir}.mp3"
                    autoplay_audio(audio_file_path)
                else:
                    text_place.success("안전합니다 !")
            else:
                text_place.success("안전합니다 !")
