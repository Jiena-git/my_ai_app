import time
from fastapi import FastAPI
from ai.detect import detect_people
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

last_count = 0
last_image = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/detect")
def detect(image_name: str):
    start = time.time()

    path = f"data/images/{image_name}"

    try:
        count = detect_people(path)
    except Exception as e:
        print("error:", e)
        count = 0

    if count is None:
        count = 0

    print("inference time:", time.time() - start)

    return {
        "person_count": int(count),
        "image": image_name
    }