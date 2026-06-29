import os
from ai.detect import detect_image


class FrameEngine:

    def __init__(self):

        self.images = []

        self.index = 0

        self.load()


    def load(self):

        path = "data/images"

        self.images = sorted([
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith((".jpg", ".png"))
        ])

        print("共加载图片：", len(self.images))


    def next_frame(self):

        if len(self.images) == 0:

            return {
                "error": "no images"
            }

        img = self.images[self.index]

        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        print("当前帧：", os.path.basename(img))

        return detect_image(img)


engine = FrameEngine()