# from fastapi import APIRouter, Body  # ← Body 추가!
# from dto.predict_dto import PredictRequest
# from controller.predict_controller import predict_fire
# from util.json_utils import sanitize_json # 혹은 farsite_service에서 직접
#
#
# router = APIRouter()
#
# @router.post("/input")
# async def predict_endpoint(req: PredictRequest = Body(...)):
#     print("✅ /input 엔드포인트 호출됨")
#     try:
#         result = await predict_fire(req)
#         print("프론트에서 받은 값:", result)
#
#         # ✅ NaN/inf 처리
#         sanitized = sanitize_json(result)
#         return sanitized
#
#     except Exception as e:
#         print(f"❌ 예측 처리 중 에러 발생: {e}")
#         return {"error": str(e)}

from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/input")
async def predict_endpoint(request: Request):
    print("✅ /input 엔드포인트 호출됨")
    try:
        data = await request.json()
        lat = data.get('lat')
        lon = data.get('lon')
        print("👉 프론트에서 받은 값:", lat, lon)

        # ✅ 무거운 처리 생략한 간단 응답
        result = {
            "lat": lat,
            "lon": lon,
            "status": "ok"
        }
        return result  # ✅ 이 줄이 꼭 필요합니다

    except Exception as e:
        print(f"❌ 예측 처리 중 에러 발생: {e}")
        return {"error": str(e)}

@router.get("/")
def root():
    return {"message": "Wildfire backend is running"}




