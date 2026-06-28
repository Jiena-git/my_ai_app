from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from ai.detect import detect_people

app = FastAPI(title="Smart Classroom")

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 静态文件
# =========================
# data/images  -> /images
# static/result -> /result
os.makedirs("static/result", exist_ok=True)

app.mount("/images", StaticFiles(directory="data/images"), name="images")
app.mount("/result", StaticFiles(directory="static/result"), name="result")

# =========================
# 多教室缓存
# =========================
CLASSROOM_CACHE = {}


# =========================
# 检测接口
# =========================
@app.get("/detect")
def detect(
    image_name: str = Query(...),
    classroom: str = Query("A5-101")
):

    img_path = os.path.join("data", "images", image_name)

    if not os.path.exists(img_path):
        return {
            "code": 404,
            "msg": "image not found"
        }

    (
        person_count,
        phone_count,
        front_people,
        img,
        save_name
    ) = detect_people(img_path)

    # 前三排就坐率
    if person_count == 0:
        front_rate = 0
    else:
        front_rate = round(front_people * 100 / person_count, 2)

    # 注意力分析（课程设计工程版）
    attention = max(
        0,
        round(
            100 - phone_count * 10
        )
    )

    result = {
        "code": 0,
        "classroom": classroom,

        "person_count": person_count,

        "phone_count": phone_count,

        "front_people": front_people,

        "front_rate": front_rate,

        "attention": attention,

        # 前端直接显示这个地址即可
        "image":
        f"http://127.0.0.1:8000/result/{save_name}"
    }

    CLASSROOM_CACHE[classroom] = result

    return result


# =========================
# 大屏数据接口
# =========================
@app.get("/dashboard")
def dashboard():

    return {
        "code": 0,
        "data": CLASSROOM_CACHE
    }
# =========================
# 首页
# =========================
@app.get("/")
def home():

    return {
        "msg": "Smart Classroom API Running"
    }