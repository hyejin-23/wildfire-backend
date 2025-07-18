from fastapi import APIRouter, Body  # ← Body 추가!
from dto.predict_dto import PredictRequest
from controller.predict_controller import predict_fire

router = APIRouter()

@router.post("/input")
async def predict_endpoint(req: PredictRequest = Body(...)):  # ✅ async로 변경
    return await predict_fire(req)  # ✅ await 사용


