from fastapi import APIRouter, Body  # ← Body 추가!
from dto.predict_dto import PredictRequest
from controller.predict_controller import predict_fire

router = APIRouter()

@router.post("/input")
async def predict_endpoint(req: PredictRequest = Body(...)):  # ✅ async로 변경
    print("✅ /input 엔드포인트 호출됨")
    print(f"   ↳ 받은 값 lat: {req.lat}, lon: {req.lon}")  # ← 추가 추천!
    return await predict_fire(req)  # ✅ await 사용

@router.get("/")
def root():
    return {"message": "Wildfire backend is running"}



