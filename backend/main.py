from fastapi import FastAPI
from ai.detect import detect_people

app = FastAPI()

@app.get("/detect")
def detect():
    count = detect_people("data/images/PartA_00000.jpg")

    return {
        "person_count": count
    }