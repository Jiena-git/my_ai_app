from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

def detect_people(image_path):

    img = cv2.imread(image_path)

    results = model(img)

    count = 0

    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 0:
                count += 1

    return count