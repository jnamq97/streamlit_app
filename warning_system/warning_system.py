import math


# class_num , x_center, y_center, width, height
def warning_state_Algorithm(x_min, y_min, x_max, y_max, class_num, h, w):
    # setting

    y = y_min
    x = (x_min + x_max) / 2

    vision_point = w * 0.5

    section_1 = w * 0.33
    section_2 = w * 0.66
    section_3 = w

    lv1_line1 = (h * 0.5) / (w * 0.33)
    lv1_line2 = h * 0.5
    lv1_line3 = -(h * 0.5) / (w * 0.33)
    lv1_line3_b = w

    lv2_line1 = (h * 0.33) / (w * 0.163)
    lv2_line1_b = w * 0.167

    lv2_line2 = h * 0.33

    lv2_line3 = -(h * 0.33) / (w * 0.173)
    lv2_line3_b = w * 0.83

    direction_point = w * 0.3885
    direction_point_reverse = w * (1 - 0.3885)
    theta_point_x_reverse = w * 0.5 - w * 0.3885
    theta_point1_y = h * 0.5
    theta_point2_y = h * 0.33
    theta_point3_y = h * 0.16

    # Area State

    safe = 0
    lv1 = 1
    lv2 = 2

    if 0 <= x <= section_1:
        if y > lv1_line1 * x:
            state = safe
        elif lv2_line1 * (x - lv2_line1_b) < y <= lv1_line1 * x:
            state = lv1
        elif y <= lv2_line1 * (x - lv2_line1_b):
            state = lv2

    elif section_1 < x <= section_2:
        if y > lv1_line2:
            state = safe
        elif lv2_line2 < y <= lv1_line2:
            state = lv1
        elif y <= lv2_line2:
            state = lv2

    elif section_2 < x <= section_3:
        if y > lv1_line3 * (x - lv1_line3_b):
            state = safe
        elif lv2_line3 * (x - lv2_line3_b) < y <= lv1_line3 * (x - lv1_line3_b):
            state = lv1
        elif y <= lv2_line3 * (x - lv2_line3_b):
            state = lv2

    area_state = state

    ###

    # Direction State

    # center 0
    # left side 1
    # right side 2

    if x < direction_point:
        direction = 2
    elif direction_point <= x <= direction_point_reverse:
        direction = 0
    else:
        direction = 1

    direction_state = direction

    ###

    # Theta State

    cos = y / (math.sqrt((x - vision_point) ** 2 + y**2))
    theta = math.acos(cos)
    degree = math.degrees(theta)

    theta_boundary1 = math.degrees(
        math.atan(theta_point_x_reverse / theta_point1_y)
    )  # 21

    theta_boundary2 = math.degrees(
        math.atan(theta_point_x_reverse / theta_point2_y)
    )  # 30

    theta_boundary3 = math.degrees(
        math.atan(theta_point_x_reverse / theta_point3_y)
    )  # 58

    theta_in = False

    if theta_point2_y < y <= theta_point1_y:
        if degree < theta_boundary1:
            theta_in = True
        else:
            theta_in = False

    elif theta_point3_y < y <= theta_point2_y:
        if degree < theta_boundary2:
            theta_in = True
        else:
            theta_in = False

    elif y <= theta_point3_y:
        if degree < theta_boundary3:
            theta_in = True
        else:
            theta_in = False

    theta_state = theta_in

    # Warning State

    warning = 0
    if area_state == 0:  # safe
        warning = 0
    elif area_state == 1:
        if theta_state == False:
            warning = 1  # yellow
        else:
            warning = 2  # orange
    else:
        if theta_state == False:
            warning = 2  # orange
        else:
            warning = 3  # red

    # Final Warning State

    # 0 : safe
    # 1 : lv1, left
    # 2 : lv1, right
    # 3 : lv1, center
    # 4 : lv2, left
    # 5 : lv2, right
    # 6 : lv2, center
    # 7 : lv3, center

    if warning == 0:
        pass
    elif warning == 1:
        if direction == 1:
            warning = 1
        elif direction == 2:
            warning = 2
        else:
            warning = 3
    elif warning == 2:
        if direction == 1:
            warning = 4
        elif direction == 2:
            warning = 5
        else:
            warning = 6

    elif warning == 3:
        warning = 7

    return class_num, warning


if __name__ == "__main__":
    CLASSES = [
        "wheelchair",
        "truck",
        "tree_trunk",
        "traffic_sign",
        "traffic_light",
        "traffic_light_controller",
        "table",
        "stroller",
        "stop",
        "scooter",
        "potted_plant",
        "power_controller",
        "pole",
        "person",
        "parking_meter",
        "movable_signage",
        "motorcycle",
        "kiosk",
        "fire_hydrant",
        "dog",
        "chair",
        "cat",
        "carrier",
        "car",
        "bus",
        "bollard",
        "bicycle",
        "bench",
        "barricade",
    ]
    # bboxes_class = [[480,280,481,281,0,960,540],[320,200,321,201,1,960,540],[600, 200, 650, 781.68212890625, 2, 960, 540],[376, 200, 377, 201, 3, 960, 540], # 0,1,2,3 -> lv1
    #                [320,90,321,91,4,960,540],[590,90,591,91,5,960,540],[500,1,501,2,6,960,540],[480,91,481,92,7,960,540]] # 4,5,6 -> lv2 7 -> lv3
    # 박스 좌표,클래스,해상도 받았다고 생각 2차원 리스트 bboxes_class
    warning_state_list = []
    cnt = 0
    mode = "Normal Mode"

    for bbox in bboxes_class:
        class_num, state = warning_state_Algorithm(
            bbox[0], bbox[1], bbox[2], bbox[3], bbox[4], bbox[6], bbox[5]
        )
        warning_state_list.append((state, class_num))
        cnt += 1

        if cnt == len(bboxes_class):
            warning_state_list.sort(reverse=True)
            if len(warning_state_list) >= 5:  # 위험구역 안에 5개 이상 위치한다면 warning mode 발동
                if warning_state_list[4][0] >= 1:
                    mode = "Warning Mode"

            # 우측통행을 기반으로 우선순위 고려

            if warning_state_list[0][0] == 0:  # 0 : safe
                TTS = "안전"

            elif warning_state_list[0][0] == 1:  # 1 : lv1, right
                TTS = "우측" + CLASSES[class_num] + "주의"

            elif warning_state_list[0][0] == 2:  # 2 : lv1, left
                TTS = "좌측" + CLASSES[class_num] + "주의"

            elif warning_state_list[0][0] == 3:  # 3 : lv1, center
                TTS = "전방" + CLASSES[class_num] + "주의"

            elif warning_state_list[0][0] == 4:  # 4 : lv2, right
                TTS = "우측" + CLASSES[class_num] + "경고"

            elif warning_state_list[0][0] == 5:  # 5 : lv2, left
                TTS = "좌측" + CLASSES[class_num] + "경고"

            elif warning_state_list[0][0] == 6:  # 6 : lv2, center
                TTS = "전방" + CLASSES[class_num] + "경고"

            elif warning_state_list[0][0] == 7:  # 7 : lv3, center
                TTS = "전방" + CLASSES[class_num] + "위험"

            print(TTS)
