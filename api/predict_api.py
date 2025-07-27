from fastapi import APIRouter, Body  # ← Body 추가!
from dto.predict_dto import PredictRequest
from controller.predict_controller import predict_fire
from util.json_utils import sanitize_json # 혹은 farsite_service에서 직접
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

from fastapi import APIRouter
from controller.predict_controller import predict_fire
from fastapi import Request

router = APIRouter()

@router.post("/input")
async def predict_endpoint(request: Request):
    print("✅ /input 엔드포인트 호출됨")
    try:
        data = await request.json()
        lat = data.get('lat')
        lon = data.get('lon')
        print("👉 프론트에서 받은 값:", lat, lon)

        # ✅ 여기서 기존 로직 호출
        result = await predict_fire(lat, lon)  # predict_fire를 lat/lon 받도록 수정하거나 wrapper 함수 작성
        print("🔥 예측 결과:", result)

        return result

    except Exception as e:
        print(f"❌ 예측 처리 중 에러 발생: {e}")
        return {"error": str(e)}

@router.get("/")
def root():
    return {"message": "Wildfire backend is running"}




