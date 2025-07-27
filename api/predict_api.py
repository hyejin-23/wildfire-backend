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

from fastapi import APIRouter, Request
from dto.predict_dto import PredictRequest
from controller.predict_controller import predict_fire
from util.json_utils import sanitize_json

import os, json, tempfile
from google.cloud import firestore

# ✅ Firebase 인증 키 환경변수 처리
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    key_dict = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
    with open(temp_path, "w") as f:
        json.dump(key_dict, f)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path

router = APIRouter()

# ✅ 기존 방식: 프론트가 직접 위도/경도 보내는 방식 유지
@router.post("/input")
async def predict_endpoint(request: Request):
    print("✅ /input 엔드포인트 호출됨")
    try:
        data = await request.json()
        lat = data.get('lat')
        lon = data.get('lon')
        print("👉 프론트에서 받은 값:", lat, lon)

        if lat is None or lon is None:
            return {"error": "lat 또는 lon 값이 누락되었습니다."}

        req_obj = PredictRequest(lat=lat, lon=lon)
        result = await predict_fire(req_obj)
        return sanitize_json(result)

    except Exception as e:
        print(f"❌ 예측 처리 중 에러 발생: {e}")
        return {"error": str(e)}


# ✅ 새로운 방식: Firebase에서 최근 위치 가져오는 엔드포인트 추가
db = firestore.Client()

@router.get("/firebase-input")
async def predict_from_firebase():
    try:
        print("🚀 /firebase-input 호출됨")

        # ✅ 최근 위치 문서 가져오기
        docs = db.collection("fire_locations")\
            .order_by("timestamp", direction=firestore.Query.DESCENDING)\
            .limit(1).stream()

        doc = next(docs, None)

        if not doc:
            print("⚠️ Firebase 문서 없음")
            return {"error": "Firebase에 저장된 위치 정보가 없습니다."}

        data = doc.to_dict()
        lat = data.get("lat")
        lon = data.get("lon")

        print(f"📡 Firestore에서 가져온 위치: lat={lat}, lon={lon}")

        if lat is None or lon is None:
            return {"error": "Firestore 문서에 lat 또는 lon 값이 없습니다."}

        # ✅ 예측 실행
        req_obj = PredictRequest(lat=lat, lon=lon)
        result = await predict_fire(req_obj)
        print("✅ 예측 완료")
        return sanitize_json(result)

    except Exception as e:
        print("❌ Firebase 예측 처리 중 오류:", e)
        return {"error": str(e)}
@router.get("/")
def root():
    return {"message": "Wildfire backend is running"}





