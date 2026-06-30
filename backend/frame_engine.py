import os
import cv2
import time
from ai.detect import detect_image


class FrameEngine:

    def __init__(self):
        self.images = []
        self.index = 0

        self.last_frame = None
        self.last_result = None

        self.load()

    def load(self):
        path = "data/images"
        self.images = sorted([
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith((".jpg", ".png"))
        ])
        print("images:", len(self.images))

    # ========================
    # YOLO线程调用
    # ========================
    def process_next(self):

        img_path = self.images[self.index]
        self.index = (self.index + 1) % len(self.images)

        result = detect_image(img_path)

        # 直接缓存“真实frame”
        self.last_frame = cv2.imread("static/cache/frame.jpg")
        self.last_result = result

        return result

    # ========================
    # MJPEG用
    # ========================
    def get_frame(self):
        return self.last_frame

    def get_result(self):
        return self.last_result


engine = FrameEngine()