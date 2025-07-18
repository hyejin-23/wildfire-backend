from dto.predict_dto import PredictRequest
from service.predict_service import process_prediction

async def predict_fire(req: PredictRequest):  # ✅ async로 변경
    return await process_prediction(req.lat, req.lon)  # ✅ await 사용


