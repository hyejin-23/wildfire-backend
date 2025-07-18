# service/ai_service.py
import requests

def send_to_ai_model(data: list):
    """
    21개 필드 JSON 리스트를 외부 AI 예측 서버로 전송
    """
    url = "https://firespread-api.onrender.com/input"
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.status_code
    except Exception as e:
        print(f"AI 예측 서버 전송 실패: {e}")
        return None

