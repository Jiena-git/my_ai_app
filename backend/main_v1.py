from fastapi import FastAPI
from ultralytics import YOLO
import cv2

app = FastAPI()

model = YOLO("yolov8n.pt")


@app.get("/")
def home():
    return {"message": "Smart Classroom API"}


@app.get("/detect")
def detect():

    image_path = "data/images/PartA_00000.jpg"

    img = cv2.imread(image_path)

    results = model(img)

    PERSON_CLASS = 0

    count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])

            if cls == PERSON_CLASS:
                count += 1

    return {
        "person_count": count
    }
