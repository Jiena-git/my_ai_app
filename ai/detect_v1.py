import cv2
from ultralytics import YOLO
import base64
import numpy as np

# =========================
# 1️⃣ 加载模型（可以换 yolov8n.pt / yolov8s.pt）
# =========================
model = YOLO("yolov8n.pt")

# =========================
# 2️⃣ 主检测函数
# =========================
def detect_people(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return None

    h, w = img.shape[:2]

    results = model(img)[0]

    person_count = 0
    phone_count = 0

    front_people = 0  # 前排人数

    boxes = results.boxes

    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        # 过滤低置信度（👉 可调）
        if conf < 0.4:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        label = model.names[cls]

        # =========================
        # 3️⃣ 人数统计
        # =========================
        if label == "person":
            person_count += 1

            # =========================
            # 4️⃣ 前排判断（核心逻辑）
            # 👉 前30%画面认为是前排
            # =========================
            if y2 < h * 0.4:
                front_people += 1

            color = (0, 255, 0)

        # =========================
        # 5️⃣ 手机检测
        # =========================
        elif label == "cell phone":
            phone_count += 1
            color = (0, 0, 255)

        else:
            continue

        # =========================
        # 6️⃣ 画框
        # =========================
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # =========================
    # 7️⃣ 编码图片返回前端
    # =========================
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode()

    return {
        "person_count": person_count,
        "phone_count": phone_count,
        "front_people": front_people,
        "image": img_base64
    }


# =========================
# 8️⃣ 本地测试入口（可删）
# =========================
if __name__ == "__main__":
    result = detect_people("test.jpg")
    print(result)