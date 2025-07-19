from fastapi import APIRouter, Body  # ← Body 추가!
from dto.predict_dto import PredictRequest
from controller.predict_controller import predict_fire

router = APIRouter()

@router.post("/input")
async def predict_endpoint(req: PredictRequest = Body(...)):
    print("✅ /input 엔드포인트 호출됨")
    try:
        return await predict_fire(req)
    except Exception as e:
        print(f"❌ 예측 처리 중 에러 발생: {e}")
        return {"error": str(e)}


@router.get("/")
def root():
    return {"message": "Wildfire backend is running"}



