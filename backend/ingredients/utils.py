import requests
from django.conf import settings


def fetch_drug_from_api(item_name):
    url = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

    params = {
        "serviceKey": settings.E_DRUG_API_KEY,
        "itemName": item_name,
        "type": "json"
    }

    response = requests.get(url, params=params)

    # 1️⃣ HTTP 에러 체크
    if response.status_code != 200:
        raise Exception(f"외부 API 요청 실패: {response.status_code}")

    # 2️⃣ JSON 변환 체크
    try:
        return response.json()
    except ValueError:
        raise Exception("외부 API 응답이 JSON이 아닙니다")
# utils.py 또는 settings.py
print("E_DRUG_API_KEY:", settings.E_DRUG_API_KEY)
