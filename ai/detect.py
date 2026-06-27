from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

def detect_people(image_path):

    img = cv2.imread(image_path)

    results = model(img, imgsz=1280,conf=0.25, iou=0.5) #results = model(img)

    count = 0

    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls == 0 and conf > 0.25:
                count += 1

    return count