from gtts import gTTS
import os


def text_to_speech(text, output_file):
    tts = gTTS(text, lang="ko")
    tts.save(output_file)
    # os.system("start " + output_file)  # 생성된 오디오 파일 실행


# 텍스트를 입력받고 TTS로 변환하여 출력합니다.
# text = input("변환할 텍스트를 입력하세요: ")
# output_file = "output.mp3"

# CLASSES_ENG = [
#     "wheelchair",
#     "truck",
#     "tree_trunk",
#     "traffic_sign",
#     "traffic_light",
#     "traffic_light_controller",
#     "table",
#     "stroller",
#     "stop",
#     "scooter",
#     "potted_plant",
#     "power_controller",
#     "pole",
#     "person",
#     "parking_meter",
#     "movable_signage",
#     "motorcycle",
#     "kiosk",
#     "fire_hydrant",
#     "dog",
#     "chair",
#     "cat",
#     "carrier",
#     "car",
#     "bus",
#     "bollard",
#     "bicycle",
#     "bench",
#     "barricade",
# ]
# CLASSES = [
#     "휠체어",
#     "트럭",
#     "나무",
#     "교통표지판",
#     "신호등",
#     "신호등제어기",
#     "탁자",
#     "유모차",
#     "정지표시판",
#     "스쿠터",
#     "화분",
#     "전원컨트롤러",
#     "기둥",
#     "사람",
#     "주차정산기",
#     "이동표지판",
#     "오토바이",
#     "키오스크",
#     "소화전",
#     "개",
#     "의자",
#     "고양이",
#     "캐리어",
#     "자동차",
#     "버스",
#     "볼라드",
#     "자전거",
#     "벤치",
#     "바리케이트",
# ]

# DIRECTIONS = ["전방", "우측", "좌측"]
# DIRECTIONS_ENG = ["center", "right", "left"]

# LEVELS = ["주의", "경고", "위험"]

# for i_dir, dir in enumerate(DIRECTIONS):
#     for i_lv, lv in enumerate(LEVELS):
#         for i_cls, cls in enumerate(CLASSES):
#             file_name = (
#                 "/opt/ml/streamlit_app/webcam/webrtc/tts/"
#                 + CLASSES_ENG[i_cls]
#                 + "_"
#                 + str(i_lv + 1)
#                 + "_"
#                 + DIRECTIONS_ENG[i_dir]
#                 + ".mp3"
#             )
#             text = f"{dir} {cls}{lv}"
#             text_to_speech(text, file_name)

text_to_speech("워닝모드", "/opt/ml/streamlit_app/webcam/webrtc/tts/warning_mode.mp3")
