# ========================
# DRF 기본
# ========================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# ========================
# Django 기본
# ========================
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Avg, Count, Q, F, FloatField, ExpressionWrapper

# ========================
# 외부 / 유틸
# ========================
import json
import requests
import logging

# ========================
# 로컬 앱
# ========================
from .models import (
    Drug,
    DrugAiSummary,   
    Symptom,
    DrugReaction,
)
from .utils import fetch_drug_from_api
from .serializers import (
    DrugSerializer,
    SymptomSerializer,
    DrugCommentSerializer,
    DrugReactionSerializer,
    DrugDetailSerializer,
)


logger = logging.getLogger(__name__)

# Gemini 이미지 생성 엔드포인트
GMS_GEMINI_IMAGE_URL = "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"
GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
# gpt 호출 함수
def call_gpt_for_drug_summary(drug):
    developer_msg = """
너는 한국어로 약 정보를 쉽게 설명해주는 AI야.
반드시 JSON만 출력해야 해.

{
  "one_liner": "",
  "easy_explain": "",
  "key_points": [],
  "cautions": [],
  "when_to_see_doctor": []
}
""".strip()

    user_msg = f"""
약 이름: {drug.name}
효능: {drug.effect}
복용법: {drug.usage}
주의사항: {drug.warning}
""".strip()


    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "developer", "content": developer_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.2,
    }

    r = requests.post(
        GMS_OPENAI_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.GMS_KEY}",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


# ================================
# 💬 약 댓글 작성 (로그인 필수)
# ================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_drug_comment(request, pk):
    """
    POST /drugs/<pk>/comments/
    - 로그인한 사용자만 댓글 작성 가능
    - author는 request.user로 강제 지정 (프론트에서 못 바꿈)
    """
    drug = get_object_or_404(Drug, pk=pk)

    serializer = DrugCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        author=request.user,
        drug=drug
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ================================
# 🔍 약 이름으로 검색 + DB 저장
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def save_drug_by_name(request):
    """
    GET /drugs/save/?name=타이레놀
    - 외부 공공 API 호출
    - DB에 없으면 저장
    - 검색 결과 리스트 반환
    """
    name = request.query_params.get('name')

    if not name:
        return Response(
            {'error': 'name 파라미터가 필요합니다.'},
            status=400
        )

    # 1️⃣ 외부 API 호출
    try:
        data = fetch_drug_from_api(name)
    except Exception as e:
        logger.exception('외부 API 호출 중 예외 발생')
        err = str(e)

        # 인증 관련 에러 구분
        if '401' in err or 'Unauthorized' in err or '인증' in err:
            return Response(
                {'error': '외부 API 인증 실패: E_DRUG_API_KEY를 확인하세요.'},
                status=502
            )

        return Response(
            {'error': f'외부 API 호출 실패: {err}'},
            status=502
        )

    body = data.get('body', {})
    items = body.get('items', [])

    # API 응답이 dict 형태일 경우 보정
    if isinstance(items, dict):
        items = items.get('item', [])

    # 검색 결과가 없는 경우도 정상 응답
    if not items:
        return Response(
            {'message': '검색 결과가 없습니다.', 'saved_count': 0},
            status=200
        )

    saved = []
    failed = []

    # 2️⃣ 하나라도 성공하면 전체 성공 처리
    for item in items:
        try:
            item_name = item.get('itemName')
            if not item_name:
                continue

            # 동일 이름의 약이 있으면 재사용
            drug, created = Drug.objects.get_or_create(
                name=item_name,
                defaults={
                    'effect': item.get('efcyQesitm', ''),
                    'usage': item.get('useMethodQesitm', ''),
                    'warning': item.get('atpnWarnQesitm', ''),
                    'image_url': item.get('itemImage', ''),
                }
            )

            saved.append({
                'id': drug.id,
                'name': drug.name,
                'created': created,
                'image_url': drug.image_url,
            })

        except Exception as e:
            # 개별 실패는 전체 실패로 보지 않음
            failed.append(str(e))

    return Response(
        {
            'saved_count': len(saved),
            'saved': saved,
            'failed_count': len(failed),
        },
        status=200
    )


# ================================
# 📄 약 상세 조회
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def drug_detail(request, pk):
    """
    GET /drugs/<pk>/
    - 약 상세 정보
    - 효능 / 용법 / 주의사항 / 평균 평점 / 댓글 포함
    """
    drug = get_object_or_404(Drug, pk=pk)
    serializer = DrugDetailSerializer(drug)
    return Response(serializer.data)


# ================================
# 🤕 증상 기반 약 추천
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_by_symptom(request):
    """
    GET /drugs/recommend/?symptom=1
    - 특정 증상에 연결된 약 목록 반환
    """
    symptom_id = request.query_params.get('symptom')

    if not symptom_id:
        return Response({'error': 'symptom 파라미터 필요'}, status=400)

    symptom = get_object_or_404(Symptom, pk=symptom_id)
    drugs = symptom.drugs.all()

    serializer = DrugSerializer(drugs, many=True)
    return Response({
        'symptom': symptom.name,
        'recommendations': serializer.data
    })


# ================================
# 📋 증상 목록 조회
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def symptom_list(request):
    """
    GET /symptoms/
    - 전체 증상 목록 반환
    """
    symptoms = Symptom.objects.all()
    serializer = SymptomSerializer(symptoms, many=True)
    return Response(serializer.data)


# ================================
# 👍👎 사용자 반응 (도움됐어요)
# ================================
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def drug_reaction(request, drug_id):
    """
    GET  /drugs/<id>/reaction/
    - 도움됨 / 도움안됨 개수
    - 로그인 시 내 반응도 함께 반환

    POST /drugs/<id>/reaction/
    - 로그인 필수
    - 같은 버튼 다시 누르면 반응 취소
    """
    drug = get_object_or_404(Drug, pk=drug_id)

    # ---------- GET ----------
    if request.method == 'GET':
        summary = (
            DrugReaction.objects
            .filter(drug=drug)
            .values('reaction')
            .annotate(count=Count('id'))
        )

        data = {
            'helpful': 0,
            'unhelpful': 0,
            'my_reaction': None,
        }

        for item in summary:
            data[item['reaction']] = item['count']

        if request.user.is_authenticated:
            my = DrugReaction.objects.filter(
                user=request.user,
                drug=drug
            ).first()
            data['my_reaction'] = my.reaction if my else None

        return Response(data)

    # ---------- POST ----------
    if not request.user.is_authenticated:
        return Response(
            {'detail': '로그인이 필요합니다.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    reaction_type = request.data.get('reaction')

    # 반응 취소
    if reaction_type is None:
        DrugReaction.objects.filter(
            user=request.user,
            drug=drug
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if reaction_type not in ['helpful', 'unhelpful']:
        return Response(
            {'detail': 'reaction 값은 helpful 또는 unhelpful 이어야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reaction_obj, _ = DrugReaction.objects.update_or_create(
        user=request.user,
        drug=drug,
        defaults={'reaction': reaction_type}
    )

    serializer = DrugReactionSerializer(reaction_obj)
    return Response(serializer.data)


# ================================
# 📊 약 목록 + 정렬
# ================================
@api_view(['GET'])
def drug_list(request):
    """
    GET /drugs/?order=helpful|rating
    - 기본순 / 도움순 / 평점순 정렬
    - 도움됐어요 비율 계산
    """
    order = request.query_params.get('order')

    drugs = Drug.objects.annotate(
        avg_rating=Avg('comments__rating'),
        helpful_count=Count(
            'reactions',
            filter=Q(reactions__reaction='helpful')
        ),
        unhelpful_count=Count(
            'reactions',
            filter=Q(reactions__reaction='unhelpful')
        ),
    ).annotate(
        # 도움됐어요 비율 (%)
        helpful_ratio=ExpressionWrapper(
            100.0 * F('helpful_count') /
            (F('helpful_count') + F('unhelpful_count')),
            output_field=FloatField()
        )
    )

    if order == 'helpful':
        drugs = drugs.order_by('-helpful_ratio')
    elif order == 'rating':
        drugs = drugs.order_by('-avg_rating')
    else:
        drugs = drugs.order_by('-id')

    serializer = DrugSerializer(drugs, many=True)
    return Response(serializer.data)

# 텍스트
@api_view(["GET"])
@permission_classes([AllowAny])
def drug_ai_summary(request, pk):
    drug = get_object_or_404(Drug, pk=pk)

    # 1️⃣ 캐시 먼저 확인
    try:
        summary = drug.ai_summary
        return Response({
            "one_liner": summary.one_liner,
            "easy_explain": summary.easy_explain,
            "key_points": summary.key_points,
            "cautions": summary.cautions,
            "when_to_see_doctor": summary.when_to_see_doctor,
            "cached": True,
            "updated_at": summary.updated_at,
        })
    except DrugAiSummary.DoesNotExist:
        pass

    # 2️⃣ GPT 호출

    try:
        parsed = call_gpt_for_drug_summary(drug)
    except Exception as e:
        return Response(
            {
                "detail": "AI 요약 생성 실패",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 3️⃣ DB 저장
    summary = DrugAiSummary.objects.create(
        drug=drug,
        one_liner=parsed.get("one_liner", ""),
        easy_explain=parsed.get("easy_explain", ""),
        key_points=parsed.get("key_points", []),
        cautions=parsed.get("cautions", []),
        when_to_see_doctor=parsed.get("when_to_see_doctor", []),
    )

    return Response({
        "one_liner": summary.one_liner,
        "easy_explain": summary.easy_explain,
        "key_points": summary.key_points,
        "cautions": summary.cautions,
        "when_to_see_doctor": summary.when_to_see_doctor,
        "cached": False,
        "updated_at": summary.updated_at,
    })





# 이미지
@api_view(["POST"])
@permission_classes([AllowAny])
def drug_ai_image(request, pk):
    """
    POST /drugs/<pk>/ai-image/
    - Gemini 2.0 Flash Exp Image Generation으로 의학 인포그래픽 생성
    """
    drug = get_object_or_404(Drug, pk=pk)
    one_liner = ""
    cautions = []
    
    # 1️⃣ AI 요약 로드 (없으면 기본값 사용)
    try:
        summary = drug.ai_summary
        one_liner = summary.one_liner
        cautions = summary.cautions
        logger.info(f"AI 요약 사용 - Drug: {drug.name}")
    except DrugAiSummary.DoesNotExist:
        one_liner = drug.effect[:100] if drug.effect else "증상 완화"
        cautions = []
        logger.info(f"AI 요약 없음, 기본값 사용 - Drug: {drug.name}")

    # 2️⃣ 영어 프롬프트 작성 (이미지 생성 모델은 영어가 더 효과적)
    image_prompt = f"""Create a medical infographic illustration:

Medicine: {drug.name}
Main Effect: {one_liner}
Details: {drug.effect[:200] if drug.effect else 'General symptom relief'}
Cautions: {', '.join(cautions[:2]) if cautions else 'Standard precautions'}

Visual Requirements:
- Full human body (front view, standing position)
- Soft GREEN GLOW on body areas where symptoms are relieved
- Soft RED GLOW on areas with potential side effects
- White or light gray background
- Flat medical illustration, infographic style
- Label major organs in Korean (한국어)
- Clean, professional, high clarity
- Gradient effect: colors fade as distance increases from affected areas
- NO scary or exaggerated expressions

Style: flat medical illustration, infographic, clean, professional
"""

    logger.info(f"=== 이미지 생성 시작: {drug.name} ===")
    logger.info(f"프롬프트 길이: {len(image_prompt)} chars")
    
    # 3️⃣ Gemini API 호출 (핵심: responseModalities를 ["Text", "Image"]로 지정)
    gemini_payload = {
        "contents": [{
            "parts": [{
                "text": image_prompt
            }]
        }],
        "generationConfig": {
            "responseModalities": ["Text", "Image"]  # ⭐ Text와 Image 둘 다 요청
        }
    }

    try:
        res = requests.post(
            GMS_GEMINI_IMAGE_URL,
            params={"key": settings.GMS_KEY},
            json=gemini_payload,
            timeout=60,
        )
        
        logger.info(f"Gemini 응답 상태: {res.status_code}")

        if res.status_code != 200:
            # 에러 응답 상세 로깅
            try:
                error_data = res.json()
                logger.error(f"Gemini 에러 JSON: {error_data}")
            except:
                logger.error(f"Gemini 에러 TEXT: {res.text[:500]}")
            
            return Response(
                {
                    "detail": "이미지 생성 실패",
                    "status_code": res.status_code,
                    "error": res.text[:500],
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        data = res.json()
        logger.info(f"응답 키: {list(data.keys())}")

        # 4️⃣ base64 이미지 추출
        if "candidates" not in data:
            logger.error(f"candidates 없음. 응답: {str(data)[:300]}")
            return Response(
                {
                    "detail": "이미지 생성 실패: 잘못된 응답 형식",
                    "response": str(data)[:500]
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        parts = data["candidates"][0]["content"]["parts"]
        logger.info(f"Parts 개수: {len(parts)}")
        
        # 각 part를 순회하며 이미지 찾기
        for i, p in enumerate(parts):
            logger.info(f"Part {i} 키: {list(p.keys())}")
            
            if "inlineData" in p:
                mime_type = p["inlineData"]["mimeType"]
                base64_data = p["inlineData"]["data"]
                logger.info(f"✅ 이미지 생성 성공! MIME: {mime_type}, 크기: {len(base64_data)} chars")
                
                return Response({
                    "mime_type": mime_type,
                    "base64": base64_data,
                })

        # 이미지가 없고 텍스트만 있는 경우
        logger.warning("이미지 없음, 텍스트만 반환됨")
        text_content = ""
        for p in parts:
            if "text" in p:
                text_content = p["text"][:200]
                break
        
        return Response(
            {
                "detail": "이미지 생성 실패: Gemini가 텍스트만 반환했습니다.",
                "text_preview": text_content
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    except requests.exceptions.Timeout:
        logger.error("Gemini API 타임아웃 (60초)")
        return Response(
            {"detail": "이미지 생성 시간 초과"},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    
    except requests.exceptions.RequestException as e:
        logger.exception("Gemini API 네트워크 에러")
        return Response(
            {"detail": f"네트워크 오류: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )
    
    except Exception as e:
        logger.exception(f"예상치 못한 오류 - Drug ID: {pk}")
        return Response(
            {"detail": "서버 내부 오류", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )