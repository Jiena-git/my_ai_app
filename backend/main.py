from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import threading
import time
import cv2

from backend.frame_engine import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# YOLO线程
# ======================
def run_engine():
    while True:
        engine.process_next()
        time.sleep(1.5)

@app.on_event("startup")
def startup():
    threading.Thread(target=run_engine, daemon=True).start()

# ======================
# JSON接口（只给数据）
# ======================
@app.get("/api/frame")
def get_frame_data():
    data = engine.get_result()
    if not data:
        return {"status": "loading"}

    return JSONResponse(data)

# ======================
# MJPEG（只给视频）
# ======================
@app.get("/api/mjpeg")
def mjpeg():

    def gen():
        while True:

            frame = engine.get_frame()

            if frame is None:
                time.sleep(0.03)
                continue

            _, buffer = cv2.imencode(".jpg", frame)

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

            time.sleep(0.03)

    return StreamingResponse(
        gen(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )