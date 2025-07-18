import requests

def send_to_ai_model(data: list):
    """
        21개 필드 JSON 리스트를 외부 AI 예측 서버로 전송
    """
    url = "https://firespread-api.onrender.com/input"
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.Timeout:
        print("AI 서버 응답 시간 초과")
        return 504
    except requests.exceptions.RequestException as e:
        print(f"AI 예측 서버 전송 실패: {e}")
        return 502


