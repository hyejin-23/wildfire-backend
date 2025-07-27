import traceback
from dto.predict_dto import PredictRequest
from service.predict_service import process_prediction

async def predict_fire(lat: float, lon: float):
    print(f"🔥 predict_fire 함수 호출됨: lat={lat}, lon={lon}")
    try:
        print("✅ [predict_controller] 요청 도착!")
        result = await process_prediction(lat, lon)
        print("✅ [predict_controller] 결과 생성 완료")
        return result
    except Exception as e:
        print("❌ [predict_controller] 예외 발생:", e)
        import traceback
        traceback.print_exc()
        return {"error": str(e)}






