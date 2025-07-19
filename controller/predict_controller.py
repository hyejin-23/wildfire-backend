import traceback
from dto.predict_dto import PredictRequest
from service.predict_service import process_prediction

async def predict_fire(req):
    try:
        print("✅ [predict_controller] 요청 도착!")
        result = await process_prediction(req.lat, req.lon)
        print("✅ [predict_controller] 결과 생성 완료")
        return result
    except Exception as e:
        print("❌ [predict_controller] 예외 발생:", e)
        traceback.print_exc()
        return {"error": str(e)}





