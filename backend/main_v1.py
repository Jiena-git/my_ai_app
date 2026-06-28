from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict
import time
import base64
import os

from ai.detect import detect_people  # 你现有的检测函数

app = FastAPI()

# =========================
# 1. CORS（前端必须）
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 2. 静态文件（用于返回标注图）
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# 3. 模拟多教室缓存（后面可换 Redis）
# =========================
CLASSROOM_CACHE: Dict[str, dict] = {}

# =========================
# 4. 核心检测接口
# =========================
@app.get("/detect")
def detect(
    image_name: str = Query(...),
    classroom: str = Query("A5-101")
):
    """
    返回：
    - 人数
    - 手机人数
    - 前排率
    - 注意力
    - 标注图片
    """
    img_path = f"data/images/{image_name}"
    # 1. YOLO检测人数
    person_count = detect_people(img_path)
    if person_count is None:
        person_count = 0
    # 2. TODO: 后续换真实模型
    phone_count = max(0, person_count // 8)        # 临时规则
    front_rate = min(100, person_count * 8)        # 临时规则
    attention = min(100, 100 - phone_count * 10)   # 临时规则
    # 3. 生成标注图路径（YOLO后面接这里）
    annotated_img = f"/static/result_{image_name}"
    # 4. 写入缓存（多教室）
    CLASSROOM_CACHE[classroom] = {
        "person_count": person_count,
        "phone_count": phone_count,
        "front_rate": front_rate,
        "attention": attention,
        "image": image_name,
        "timestamp": time.time(),
        "annotated_img": annotated_img
    }
    # 5. 返回前端
    return {
        "classroom": classroom,
        "person_count": person_count,
        "phone_count": phone_count,
        "front_rate": front_rate,
        "attention": attention,
        "image": image_name,
        "annotated_img": annotated_img
    }
# 5. 获取多教室数据（大屏用）
@app.get("/dashboard")
def dashboard():
    return CLASSROOM_CACHE