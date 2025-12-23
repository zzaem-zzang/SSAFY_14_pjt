# ingredients/utils.py
import requests
from django.conf import settings
from .models import Drug
from django.db import connection
from django.db.models import Q
import json

from pathlib import Path

BASE_URL = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

# 전체 약 가져오기
def fetch_all_drugs_from_api():
    """
    e약은on API에서 전체 약품 목록 가져오기 (페이지 순회)
    """
    page = 1
    all_items = []

    while True:
        params = {
            "serviceKey": settings.E_DRUG_API_KEY,
            "pageNo": page,
            "numOfRows": 100,
            "type": "json",
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            raise Exception(f"API 요청 실패: {response.status_code}")

        data = response.json()
        items = data.get("body", {}).get("items", [])

        if not items:
            break

        all_items.extend(items)
        page += 1

    return all_items


# db 캐싱 함수




def cache_drugs_on_startup():
    # ⭐ 테이블이 아직 없으면 아무 것도 하지 않음
    if 'ingredients_drug' not in connection.introspection.table_names():
        return

    # ⭐ 이미 데이터가 있으면 재캐싱 안 함
    if Drug.objects.exists():
        print("✅ Drug cache already exists")
        return

    print("🚀 Fetching drugs from e약은on API...")

    drugs = fetch_all_drugs_from_api()

    for d in drugs:
        Drug.objects.create(
            name=d.get("itemName", ""),
            effect=d.get("efcyQesitm", ""),
            usage=d.get("useMethodQesitm", ""),
            warning=d.get("atpnWarnQesitm", ""),
            image_url=d.get("itemImage")
        )

    print(f"✅ Drug cache completed ({len(drugs)} items)")


## 키워드 추출
def extract_keywords_with_ai(text):
    prompt = f"""
너는 의료 NLP 시스템이야.

아래 문장에서
✔ 일상적인 표현을
✔ 의학적으로 표준화된 증상 용어로 변환해.

반드시 effect 필드에 들어갈 수 있는
'의학 증상 명칭'만 반환해.

예시:
"머리 아파" → "두통"
"열이 나요" → "발열"
"배가 아파요" → "복통"
"속이 울렁거려요" → "오심"

반드시 JSON만 출력해.

출력 형식:
{{ "symptoms": ["두통"] }}

문장:
{text}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    res = requests.post(
        GMS_OPENAI_URL,
        headers={
            "Authorization": f"Bearer {settings.GMS_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=15
    )

    res.raise_for_status()
    content = res.json()["choices"][0]["message"]["content"]

    return json.loads(content)["symptoms"]

def search_drugs_by_effect_keywords(keywords):
    """
    effect 텍스트에 키워드가 포함된 약 검색
    """
    q = Q()
    for k in keywords:
        q |= Q(effect__icontains=k)

    return Drug.objects.filter(q).distinct()

def search_drugs_by_ai(text):
    """
    1. AI로 증상 키워드 추출
    2. effect 기반으로 약 검색
    """
    keywords = extract_keywords_with_ai(text)
    drugs = search_drugs_by_effect_keywords(keywords)
    return drugs, keywords
