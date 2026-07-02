import asyncio
import json
import os
import time
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import threading
import cv2

from backend.frame_engine import engine, CLASSROOMS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件：前端构建产物
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend-vue", "dist")
if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

DEFAULT_ROOM = CLASSROOMS[0]


def run_engine():
    while True:
        engine.process_next()
        time.sleep(1.5)


@app.on_event("startup")
def startup():
    threading.Thread(target=run_engine, daemon=True).start()


# ================================================================
# 实时单帧 / MJPEG / WebSocket（保持兼容）
# ================================================================

@app.get("/api/frame")
def get_frame_data(classroom: str = Query(default=DEFAULT_ROOM)):
    data = engine.get_result(classroom)
    if not data:
        return {"status": "loading"}
    return JSONResponse(data)


@app.get("/api/mjpeg")
def mjpeg(classroom: str = Query(default=DEFAULT_ROOM)):

    def gen():
        last_frame = None
        while True:
            frame = engine.get_frame(classroom)
            if frame is None:
                time.sleep(0.03)
                continue
            if frame is last_frame:
                time.sleep(0.03)
                continue
            last_frame = frame
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


@app.websocket("/api/ws")
async def websocket_endpoint(ws: WebSocket, classroom: str = Query(default=DEFAULT_ROOM)):
    await ws.accept()
    q = engine.subscribe(classroom)

    # 先发送当前帧
    frame = engine.get_frame(classroom)
    result = engine.get_result(classroom)
    if frame is not None and result is not None:
        _, buf = cv2.imencode(".jpg", frame)
        await ws.send_bytes(buf.tobytes())
        await ws.send_json({
            "person_count": result["person_count"],
            "phone_count": result["phone_count"],
            "front_people": result["front_people"],
            "front_rate": result.get("front_rate", 0),
            "attention": result["attention"],
        })

    try:
        while True:
            payload = await q.get()
            await ws.send_bytes(payload["image_base64"])
            await ws.send_json({
                "person_count": payload["person_count"],
                "phone_count": payload["phone_count"],
                "front_people": payload["front_people"],
                "front_rate": payload.get("front_rate", 0),
                "attention": payload["attention"],
            })
    except WebSocketDisconnect:
        pass
    finally:
        engine.unsubscribe(classroom, q)
        try:
            await ws.close()
        except Exception:
            pass


# ================================================================
# 图表数据 API（新增）
# ================================================================

@app.get("/api/timeline")
def get_timeline(classroom: str = Query(default=DEFAULT_ROOM)):
    """返回指定教室的时间序列数据（抬头率曲线）"""
    data = engine.get_timeline(classroom)
    return JSONResponse({"classroom": classroom, "points": data})


@app.get("/api/heatmap")
def get_heatmap(classroom: str = Query(default=DEFAULT_ROOM)):
    """返回指定教室的活跃度热力图数据"""
    grid = engine.get_heatmap(classroom)
    radar = engine.get_radar(classroom)
    return JSONResponse({
        "classroom": classroom,
        "grid": grid,
        "rows": 10,
        "cols": 10,
        "max_val": max(max(row) for row in grid) if grid else 0,
        "person_count": radar["person_count"],
    })


@app.get("/api/radar")
def get_radar(classroom: str = Query(default=DEFAULT_ROOM)):
    """返回指定教室的走神预警雷达图数据"""
    radar = engine.get_radar(classroom)
    return JSONResponse({
        "classroom": classroom,
        "dimensions": [
            {"name": "手机使用率", "value": radar["phone_rate"], "max": 100},
            {"name": "后排聚集度", "value": radar["back_ratio"], "max": 100},
            {"name": "人数波动", "value": radar["person_volatility"], "max": 100},
            {"name": "前排缺失", "value": radar["front_engagement"], "max": 100},
            {"name": "综合预警", "value": radar["warning_index"], "max": 100},
        ],
    })


@app.get("/api/classrooms/summary")
def get_classrooms_summary():
    """所有教室当前摘要（多班级卡片 + 对比）"""
    return JSONResponse(engine.get_all_summaries())


@app.get("/api/classrooms/compare")
def get_compare_timelines():
    """所有教室时间序列（多班级分栏对比）"""
    return JSONResponse(engine.get_compare_timelines())


@app.get("/api/classrooms/list")
def list_classrooms():
    """列出所有教室"""
    return JSONResponse([{"id": r, "name": r} for r in CLASSROOMS])


# ================================================================
# SPA 前端（放在所有 API 路由之后）
# ================================================================
@app.get("/{full_path:path}")
async def serve_spa(full_path: str = ""):
    """回退到前端 index.html（SPA 路由）"""
    index_path = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"status": "frontend not built — run: cd frontend-vue && npm run build"}
