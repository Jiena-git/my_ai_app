import os
import cv2
from ultralytics import YOLO
from ai.utils import analyse_boxes, calculate_attention, draw_boxes

MODEL_PATH = "weights/yolov8s.pt"
model = YOLO(MODEL_PATH)

CACHE_DIR = "static/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

STATS_COLOR = (255, 255, 255)  # 白色文字


def _overlay_stats(image, info, attention):
    """在画面左上角叠加统计文字，保证画面和数据永远同步"""
    h = image.shape[0]
    lines = [
        f"Phone: {info['phone_count']}",
        f"Front: {info['front_people']}",
        f"Attention: {attention}%",
    ]
    y0 = 30
    for i, line in enumerate(lines):
        y = y0 + i * 24
        cv2.putText(image, line, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
        cv2.putText(image, line, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, STATS_COLOR, 2)
    return image


def detect_frame(image):

    results = model(image, verbose=False, conf=0.02, iou=0.6)[0]

    h = image.shape[0]

    info = analyse_boxes(
        results,
        h,
        person_class=0,
        phone_class=67,
        front_ratio=0.5
    )

    # 空帧过滤：高置信度(>0.1)人数 < 3 时认为是空画面
    high_conf_persons = sum(
        1 for b in results.boxes
        if int(b.cls[0]) == 0 and float(b.conf[0]) > 0.1
    )
    is_empty = high_conf_persons < 3

    if is_empty:
        info["person_count"] = 0
        info["phone_count"] = 0
        info["front_people"] = 0
        info["front_rate"] = 0
        # 空帧直接用原图，不画框
        draw = image.copy()
    else:
        draw = draw_boxes(
            image,
            results,
            front_ratio=0.5,
            person_class=0,
            phone_class=67
        )

    attention = calculate_attention(
        info["person_count"],
        info["phone_count"]
    )

    # 在画面上叠加统计数据
    draw = _overlay_stats(draw, info, attention)

    save_path = os.path.join(CACHE_DIR, "frame.jpg")
    cv2.imwrite(save_path, draw)

    # 提取人物检测框坐标（用于热力图）
    person_boxes = []
    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        if cls == 0 and conf >= 0.03:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            person_boxes.append([x1, y1, x2, y2])

    return {
        "image": "/static/cache/frame.jpg",
        "person_count": info["person_count"],
        "phone_count": info["phone_count"],
        "front_people": info["front_people"],
        "front_rate": info.get("front_rate", 0),
        "attention": attention,
        "boxes": person_boxes,
        "frame": draw
    }


def detect_image(img_path):
    image = cv2.imread(img_path)
    return detect_frame(image)
