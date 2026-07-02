import os
import asyncio
import cv2
import time
import math
from collections import deque
from ai.detect import detect_image

CLASSROOMS = ["A5-101", "A5-102", "A5-103", "A5-104", "A5-105"]

# 每间教室保留的历史数据点数（约覆盖一节课）
MAX_HISTORY = 200
# 热力图网格大小
HEAT_GRID_ROWS = 10
HEAT_GRID_COLS = 10


def _empty_radar():
    """返回默认雷达图维度"""
    return {
        "phone_rate": 0,
        "back_ratio": 0,
        "person_volatility": 0,
        "front_engagement": 0,
        "warning_index": 0,
        "person_count": 0,
        "phone_count": 0,
        "attention": 100,
    }


def _empty_timeline_point():
    return {
        "ts": 0,
        "person_count": 0,
        "phone_count": 0,
        "front_people": 0,
        "attention": 100,
        "front_rate": 0,
    }


def _empty_heatmap():
    """返回全零热力图"""
    return [[0] * HEAT_GRID_COLS for _ in range(HEAT_GRID_ROWS)]


class FrameEngine:

    def __init__(self):
        self._pools = {}          # classroom -> [image_paths]
        self._indexes = {}        # classroom -> current index
        self._last_frames = {}    # classroom -> last annotated frame
        self._last_results = {}   # classroom -> last detection result
        self._subscribers: dict[str, list] = {}  # classroom -> [asyncio.Queue]

        # 历史数据累积
        self._timelines: dict[str, deque] = {}       # classroom -> deque of timeline points
        self._heatmaps: dict[str, list] = {}          # classroom -> 2D activity heatmap
        self._radar_cache: dict[str, dict] = {}       # classroom -> radar dimensions
        self._attention_history: dict[str, list] = {} # 用于计算注意力波动
        self._person_history: dict[str, list] = {}    # 用于计算人数波动

        self.load()

    def load(self):
        path = "data/images"
        all_images = sorted([
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith((".jpg", ".png"))
        ])
        n = len(all_images) // len(CLASSROOMS)
        for i, room in enumerate(CLASSROOMS):
            start = i * n
            end = start + n if i < len(CLASSROOMS) - 1 else len(all_images)
            self._pools[room] = all_images[start:end]
            self._indexes[room] = 0
            self._last_frames[room] = None
            self._last_results[room] = None
            self._timelines[room] = deque(maxlen=MAX_HISTORY)
            self._heatmaps[room] = _empty_heatmap()
            self._radar_cache[room] = _empty_radar()
            self._attention_history[room] = []
            print(f"  {room}: {len(self._pools[room])} 张图片")
        print(f"总计 {len(all_images)} 张图片，{len(CLASSROOMS)} 间教室")

    # ============================================================
    # 处理
    # ============================================================
    def process_next(self):
        """处理所有教室的下一帧"""
        for room in CLASSROOMS:
            pool = self._pools[room]
            if not pool:
                continue
            idx = self._indexes[room]
            img_path = pool[idx]
            self._indexes[room] = (idx + 1) % len(pool)

            result = detect_image(img_path)
            frame = result.pop("frame", None)

            self._last_frames[room] = frame
            self._last_results[room] = result

            # 累积历史数据
            self._accumulate(room, result, frame)

            # 推送给 WebSocket 订阅者
            self._notify(room, frame, result)

    def _accumulate(self, room, result, frame):
        """累积时间序列、热力图、雷达图数据"""
        h, w = frame.shape[:2] if frame is not None else (480, 640)

        # ---- 时间序列 ----
        point = {
            "ts": time.time(),
            "time_str": time.strftime("%H:%M:%S"),
            "person_count": result["person_count"],
            "phone_count": result["phone_count"],
            "front_people": result["front_people"],
            "attention": result["attention"],
            "front_rate": result.get("front_rate", 0),
        }
        self._timelines[room].append(point)

        # ---- 注意力历史（用于计算波动） ----
        self._attention_history[room].append(result["attention"])
        if len(self._attention_history[room]) > 60:
            self._attention_history[room] = self._attention_history[room][-60:]

        # ---- 人数历史（用于计算波动） ----
        if room not in self._person_history:
            self._person_history[room] = []
        self._person_history[room].append(result["person_count"])
        if len(self._person_history[room]) > 60:
            self._person_history[room] = self._person_history[room][-60:]

        # ---- 热力图 ----
        if "boxes" in result and result["boxes"]:
            grid = [[0] * HEAT_GRID_COLS for _ in range(HEAT_GRID_ROWS)]
            for box in result["boxes"]:
                # box: [x1, y1, x2, y2, cls]
                cx = (box[0] + box[2]) / 2 / w
                cy = (box[1] + box[3]) / 2 / h
                col = min(int(cx * HEAT_GRID_COLS), HEAT_GRID_COLS - 1)
                row = min(int(cy * HEAT_GRID_ROWS), HEAT_GRID_ROWS - 1)
                grid[row][col] += 1
            # 指数平滑融合
            alpha = 0.3
            self._heatmaps[room] = [
                [
                    self._heatmaps[room][r][c] * (1 - alpha) + grid[r][c] * alpha
                    for c in range(HEAT_GRID_COLS)
                ]
                for r in range(HEAT_GRID_ROWS)
            ]

        # ---- 雷达图维度 ----
        total = result["person_count"]
        phone = result["phone_count"]
        front = result["front_people"]
        attn = result["attention"]
        front_rate = result.get("front_rate", 0)

        # 1. 手机使用率（实际检测值）
        phone_rate = round(phone / total * 100, 1) if total > 0 else 0

        # 2. 后排聚集度（非前排比例 → 后排学生更难管理）
        back_ratio = round((total - front) / total * 100, 1) if total > 0 else 0

        # 3. 人数波动（最近30帧 person_count 的标准差，反映课堂躁动程度）
        recent_persons = self._person_history.get(room, [])[-30:]
        person_volatility = 0
        if len(recent_persons) >= 2:
            mean_p = sum(recent_persons) / len(recent_persons)
            var_p = sum((v - mean_p) ** 2 for v in recent_persons) / len(recent_persons)
            person_volatility = round(min(math.sqrt(var_p) / max(mean_p, 1) * 100, 100), 1)

        # 4. 前排参与度（front_rate 的反面 → 前排越少，预警越高）
        front_engagement = round(100 - front_rate, 1)

        # 5. 综合预警指数（加权平均，越高越需要关注）
        warning_index = round(
            phone_rate * 0.3 +
            back_ratio * 0.3 +
            person_volatility * 0.2 +
            front_engagement * 0.2, 1
        )

        self._radar_cache[room] = {
            "phone_rate": phone_rate,
            "back_ratio": back_ratio,
            "person_volatility": person_volatility,
            "front_engagement": front_engagement,
            "warning_index": warning_index,
            "person_count": total,
            "phone_count": phone,
            "attention": attn,
        }

    # ============================================================
    # 通知推送
    # ============================================================
    def _notify(self, room, frame, result):
        qs = self._subscribers.get(room, [])
        if not qs:
            return
        _, buf = cv2.imencode(".jpg", frame)
        payload = {
            "image_base64": buf.tobytes(),
            "person_count": result["person_count"],
            "phone_count": result["phone_count"],
            "front_people": result["front_people"],
            "attention": result["attention"],
            "front_rate": result.get("front_rate", 0),
        }
        for q in qs:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    # ============================================================
    # 订阅
    # ============================================================
    def subscribe(self, classroom):
        q = asyncio.Queue(maxsize=2)
        self._subscribers.setdefault(classroom, []).append(q)
        return q

    def unsubscribe(self, classroom, q):
        qs = self._subscribers.get(classroom, [])
        if q in qs:
            qs.remove(q)

    # ============================================================
    # 查询接口
    # ============================================================
    def get_frame(self, classroom):
        return self._last_frames.get(classroom)

    def get_result(self, classroom):
        return self._last_results.get(classroom)

    def get_timeline(self, classroom):
        """返回时间序列数据（供图表使用）"""
        return list(self._timelines.get(classroom, []))

    def get_heatmap(self, classroom):
        """返回热力图网格数据"""
        return self._heatmaps.get(classroom, _empty_heatmap())

    def get_radar(self, classroom):
        """返回雷达图维度"""
        return self._radar_cache.get(classroom, _empty_radar())

    def get_all_summaries(self):
        """返回所有教室的摘要数据（用于多班级对比）"""
        summaries = {}
        for room in CLASSROOMS:
            result = self._last_results.get(room)
            radar = self._radar_cache.get(room, _empty_radar())
            if result:
                summaries[room] = {
                    "person_count": result["person_count"],
                    "phone_count": result["phone_count"],
                    "front_people": result["front_people"],
                    "attention": result["attention"],
                    "front_rate": result.get("front_rate", 0),
                    "radar": radar,
                }
            else:
                summaries[room] = {
                    "person_count": 0,
                    "phone_count": 0,
                    "front_people": 0,
                    "attention": 100,
                    "front_rate": 0,
                    "radar": _empty_radar(),
                }
        return summaries

    def get_compare_timelines(self):
        """返回所有教室的时间序列用于对比"""
        data = {}
        for room in CLASSROOMS:
            data[room] = list(self._timelines.get(room, []))
        return data


engine = FrameEngine()
