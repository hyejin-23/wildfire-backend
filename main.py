from fastapi import FastAPI
from api.predict_api import router as predict_router

app = FastAPI()

# /input 엔드포인트 등록
app.include_router(predict_router)



