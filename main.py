from fastapi import FastAPI
from api.predict_api import router as predict_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# /input 엔드포인트 등록
app.include_router(predict_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://localhost:3000"] 등 프론트 주소 명시
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



