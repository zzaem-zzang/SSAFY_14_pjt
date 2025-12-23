# ========================
# DRF 기본
# ========================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
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
from .utils import search_drugs_by_ai


# ========================
# 로컬 앱
# ========================
from .models import (
    Drug,
    DrugAiSummary,   
    DrugReaction,
)
from .serializers import (
    DrugSerializer,
    DrugCommentSerializer,
    DrugReactionSerializer,
    DrugDetailSerializer,
)

# ========================
# qrcode
# ========================
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

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
# 📊 약 목록 + 검색 + 정렬
# ================================
@api_view(['GET'])
def drug_list(request):
    """
    GET /drugs/?search=타이레놀&order=helpful|rating
    - 약 이름 검색
    - 기본순 / 도움순 / 평점순 정렬
    """
    order = request.query_params.get('order')
    search = request.query_params.get('search')  # ⭐ 핵심 추가

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
        helpful_ratio=ExpressionWrapper(
            100.0 * F('helpful_count') /
            (F('helpful_count') + F('unhelpful_count')),
            output_field=FloatField()
        )
    )

    # ⭐⭐⭐ 약 이름 필터링 핵심 ⭐⭐⭐
    if search:
        drugs = drugs.filter(name__icontains=search)

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
        
        




@api_view(['GET'])
def drug_ai_search(request):
    """
    GET /api/drugs/ai-search/?q=머리가 지끈거리고 열나요
    """
    q = request.GET.get('q', '').strip()

    if not q:
        return Response(
            {'message': '검색어를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    drugs, symptoms = search_drugs_by_ai(q)

    serializer = DrugSerializer(drugs, many=True)
    return Response({
        "input": q,
        "detected_symptoms": symptoms,
        "count": drugs.count(),
        "results": serializer.data
    })




@api_view(['GET'])
def generate_drug_qr(request, drug_id):
    """약 정보를 QR 코드로 생성 (JSON 포맷)"""
    try:
        from .models import Drug
        drug = Drug.objects.get(pk=drug_id)
        
        # 🔥 약 정보를 JSON으로 담기
        drug_info = {
            '약품명': drug.name,
            '효능효과': drug.effect[:200] if drug.effect else '정보 없음',
            '용법용량': drug.usage[:200] if drug.usage else '정보 없음',
            '주의사항': drug.warning[:200] if drug.warning else '정보 없음',
        }
        
        # JSON을 보기 좋게 포맷팅
        qr_data = json.dumps(drug_info, ensure_ascii=False, indent=2)
        
        print(f"✅ QR에 담긴 정보:\n{qr_data}")
        
        # QR 코드 생성
        qr = qrcode.QRCode(
            version=None,  # 자동으로 크기 조정
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 이미지 생성
        img = qr.make_image(fill_color="black", back_color="white")
        
        # base64로 인코딩
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'qr_image': f'data:image/png;base64,{img_base64}',
            'drug_info': drug_info,
            'drug_name': drug.name
        })
        
    except Drug.DoesNotExist:
        return Response({'error': '약 정보를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        print(f"❌ QR 생성 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
