import traceback
from dto.predict_dto import PredictRequest
from service.predict_service import process_prediction

async def predict_fire(req: PredictRequest):
    try:
        return await process_prediction(req.lat, req.lon)
    except Exception as e:
        print("🔥 예측 처리 중 예외 발생:", e)
        traceback.print_exc()
        return {"error": str(e)}






