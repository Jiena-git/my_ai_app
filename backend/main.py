from fastapi import FastAPI
from ai.detect import detect_people
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()   #必须先创建 app
# 再加 middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/detect")
def detect():
    count = detect_people("data/images/PartA_00000.jpg")

    return {
        "person_count": count
    }