#检测课堂视频，统计人数、手机人数
from ultralytics import YOLO
import cv2

# 加载官方YOLO模型
model = YOLO("yolov8n.pt")

# 图片路径（先测试第一张）
image_path = "data/images/PartA_00000.jpg"

# 读取图片
img = cv2.imread(image_path)

# 推理
results = model(img)

# person类别编号（COCO数据集）
PERSON_CLASS = 0

count = 0

for r in results:
    for box in r.boxes:

        cls = int(box.cls[0])

        if cls == PERSON_CLASS:

            count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0,255,0),
                2
            )

# 输出人数
print("课堂人数：", count)

# 写到图片
cv2.putText(
    img,
    f"Person:{count}",
    (20,40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0,0,255),
    2
)

# 保存结果
cv2.imwrite("result.jpg", img)

print("检测完成")