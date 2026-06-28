from ultralytics import YOLO
import cv2
import os

# =========================
# 加载模型（后续可直接改成 yolov8s.pt）
# =========================
model = YOLO("yolov8n.pt")

# 保存标注图片目录
SAVE_DIR = "static/result"
os.makedirs(SAVE_DIR, exist_ok=True)


def detect_people(img_path):
    """
    返回：
    person_count
    phone_count
    front_people
    annotated_img
    saved_image_name
    """

    img = cv2.imread(img_path)

    if img is None:
        raise FileNotFoundError(f"图片不存在：{img_path}")

    height, width = img.shape[:2]

    results = model(img, verbose=False)[0]

    person_count = 0
    phone_count = 0
    front_people = 0

    # ===== 前3排分界线（可调整）=====
    front_line = int(height * 0.45)

    # 画分界线
    cv2.line(
        img,
        (0, front_line),
        (width, front_line),
        (255, 255, 0),
        2
    )

    cv2.putText(
        img,
        "Front 3 Rows",
        (20, front_line - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )

    # =========================
    # YOLO检测
    # =========================
    for box in results.boxes:

        cls = int(box.cls[0])

        conf = float(box.conf[0])

        if cls != 0:
            continue

        if conf < 0.35:
            continue

        person_count += 1

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # =========================
        # 前3排统计
        # =========================
        if cy < front_line:
            front_people += 1

        # =========================
        # 课程设计工程版：
        # 后续替换成真正手机检测
        # =========================
        label = "Person"

        color = (0, 255, 0)

        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.circle(
            img,
            (cx, cy),
            3,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            img,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    # =========================
    # 保存标注图片
    # =========================
    image_name = os.path.basename(img_path)

    save_name = "result_" + image_name

    save_path = os.path.join(SAVE_DIR, save_name)

    cv2.imwrite(save_path, img)

    return (
        person_count,
        phone_count,
        front_people,
        img,
        save_name
    )