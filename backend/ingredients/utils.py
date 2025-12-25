# ingredients/utils.py
import requests
import json
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.core.files.base import ContentFile

from .models import Drug


BASE_URL = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"


# ============================
# e약은on API 연동
# ============================
def fetch_all_drugs_from_api():
    """
    e약은on API에서 전체 의약품 목록을 페이지 단위로 순회하여 가져옴
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

        # API 요청 실패 시 예외 발생
        if response.status_code != 200:
            raise Exception(f"API 요청 실패: {response.status_code}")

        data = response.json()
        items = data.get("body", {}).get("items", [])

        # 더 이상 데이터가 없으면 종료
        if not items:
            break

        all_items.extend(items)
        page += 1

    return all_items


# ============================
# DB 캐싱
# ============================
def cache_drugs_on_startup():
    """
    서버 시작 시 Drug 테이블이 비어있으면
    e약은on API에서 데이터를 가져와 DB에 캐싱
    """
    # 테이블이 아직 생성되지 않았으면 종료
    if 'ingredients_drug' not in connection.introspection.table_names():
        return

    # 이미 데이터가 있으면 재수집하지 않음
    if Drug.objects.exists():
        print("✅ Drug cache already exists")
        return

    print("🚀 Fetching drugs from e약은on API...")

    drugs = fetch_all_drugs_from_api()

    for d in drugs:
        drug = Drug.objects.create(
            name=d.get("itemName", ""),
            effect=d.get("efcyQesitm", ""),
            usage=d.get("useMethodQesitm", ""),
            warning=d.get("atpnWarnQesitm", ""),
            image_url=d.get("itemImage"),
        )

        # 🔥 외부 이미지 URL이 있으면 이미지 파일로 저장
        if drug.image_url:
            download_and_save_image(drug, drug.image_url)

    print(f"✅ Drug cache completed ({len(drugs)} items)")


# ============================
# AI 기반 키워드 추출
# ============================
def extract_keywords_with_ai(text):
    """
    사용자 자연어 문장에서
    - 일상 표현 → 의학적으로 표준화된 증상 키워드로 변환
    - JSON 형식으로만 응답받음
    """
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

    # HTTP 에러 발생 시 예외
    res.raise_for_status()

    content = res.json()["choices"][0]["message"]["content"]

    # JSON 문자열 → dict → symptoms 리스트 반환
    return json.loads(content)["symptoms"]


# ============================
# 약 검색 로직
# ============================
def search_drugs_by_effect_keywords(keywords):
    """
    effect 텍스트에 키워드가 포함된 의약품 검색
    """
    q = Q()
    for k in keywords:
        q |= Q(effect__icontains=k)

    return Drug.objects.filter(q).distinct()


def search_drugs_by_ai(text):
    """
    1. AI로 증상 키워드 추출
    2. effect 필드 기반으로 의약품 검색
    """
    keywords = extract_keywords_with_ai(text)
    drugs = search_drugs_by_effect_keywords(keywords)
    return drugs, keywords


# ============================
# 이미지 다운로드
# ============================
def download_and_save_image(drug, image_url):
    """
    외부 이미지 URL을 다운로드하여
    Drug.image 필드에 파일로 저장
    """
    try:
        res = requests.get(image_url, timeout=10)
        if res.status_code != 200:
            return

        filename = image_url.split('/')[-1] + '.jpg'
        drug.image.save(
            filename,
            ContentFile(res.content),
            save=True
        )

    except Exception as e:
        print(f"❌ 이미지 저장 실패: {drug.name}", e)
