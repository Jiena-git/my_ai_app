from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.frame_engine import engine
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 关键：必须挂静态目录，否则图片永远404
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/frame")
def api_frame():
    return engine.next_frame()