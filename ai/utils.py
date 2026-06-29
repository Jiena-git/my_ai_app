import cv2

# ======================================================
# 分析检测框
# ======================================================
def analyse_boxes(
    result,
    image_height,
    person_class,
    phone_class,
    front_ratio
):
    """
    返回：

    {
        person_count,
        phone_count,
        front_people,
        front_rate
    }
    """
    person_count = 0
    phone_count = 0
    front_people = 0

    front_line = int(image_height * front_ratio)

    for box in result.boxes:

        cls = int(box.cls[0])

        conf = float(box.conf[0])

        if conf < 0.35:
            continue

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        # 人
        if cls == person_class:

            person_count += 1

            center_y = (y1 + y2) // 2

            if center_y < front_line:
                front_people += 1

        # 手机
        elif cls == phone_class:

            phone_count += 1

    if person_count == 0:

        front_rate = 0

    else:

        front_rate = round(
            front_people / person_count * 100,
            2
        )

    return {

        "person_count": person_count,

        "phone_count": phone_count,

        "front_people": front_people,

        "front_rate": front_rate

    }

# ======================================================
# 绘制检测框
# ======================================================
def draw_boxes(

    image,

    result,

    front_ratio,

    person_class,

    phone_class

):
    draw = image.copy()

    h, w = draw.shape[:2]

    front_line = int(h * front_ratio)

    # 前3排分界线
    cv2.line(

        draw,

        (0, front_line),

        (w, front_line),

        (255, 255, 0),

        2

    )

    cv2.putText(

        draw,

        "Front 3 Rows",

        (10, front_line - 10),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (255, 255, 0),

        2

    )

    for box in result.boxes:

        cls = int(box.cls[0])

        conf = float(box.conf[0])

        if conf < 0.35:
            continue

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        # 人
        if cls == person_class:

            color = (0, 255, 0)

            label = "person"

        # 手机
        elif cls == phone_class:

            color = (0, 0, 255)

            label = "Phone"

        else:

            continue

        cv2.rectangle(

            draw,

            (x1, y1),

            (x2, y2),

            color,

            2

        )

        cv2.putText(

            draw,

            label,

            (x1, max(25, y1 - 5)),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            color,

            2

        )

    return draw


# ======================================================
# 注意力分析
# ======================================================
def calculate_attention(

    person_count,

    phone_count

):

    if person_count == 0:

        return 100

    rate = phone_count / person_count

    attention = 100 - rate * 100

    attention = max(0, min(100, attention))

    return round(attention, 1)