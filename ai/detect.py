import os
import cv2
from ultralytics import YOLO
from ai.utils import analyse_boxes, calculate_attention, draw_boxes

MODEL_PATH = "weights/yolov8n.pt"

model = YOLO(MODEL_PATH)

CACHE_DIR = "static/cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def detect_image(img_path):

    image = cv2.imread(img_path)

    results = model(image, verbose=False)[0]

    h = image.shape[0]

    info = analyse_boxes(
        results,
        h,
        person_class=0,
        phone_class=67,
        front_ratio=0.3
    )

    attention = calculate_attention(
        info["person_count"],
        info["phone_count"]
    )

    draw = draw_boxes(
        image,
        results,
        front_ratio=0.3,
        person_class=0,
        phone_class=67
    )

    save_path = os.path.join(CACHE_DIR, "frame.jpg")

    cv2.imwrite(save_path, draw)

    return {
        "image": "/static/cache/frame.jpg",
        "person_count": info["person_count"],
        "phone_count": info["phone_count"],
        "front_people": info["front_people"],
        "attention": attention
    }