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
#  약 댓글 작성 (로그인 필수)
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
#  약 상세 조회 (조회수 포함)
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def drug_detail(request, pk):
    """
    GET /drugs/<pk>/
    - 약 상세 정보
    - 조회수 증가
    """
    drug = get_object_or_404(Drug, pk=pk)

    #  조회수 증가
    Drug.objects.filter(pk=pk).update(
        view_count=F('view_count') + 1
    )

    # 최신 값 다시 가져오기
    drug.refresh_from_db()

    serializer = DrugDetailSerializer(drug)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_drugs_by_view(request):
    """
    GET /api/drugs/popular/views/
    - 조회수 기준 인기 약 TOP 10
    """
    drugs = Drug.objects.order_by('-view_count')[:10]
    serializer = DrugSerializer(drugs, many=True)
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

    # 약 이름 필터링 핵심 
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


# ai 챗봇 
SYSTEM_PROMPT = """
너는 의약품 정보를 친절하게 설명해주는 AI 어시스턴트야.
전문 용어는 최대한 쉽게 풀어서 설명해 줘.
이 약과 직접 관련 없는 내용은 추측하지 말고,
의학적 판단이나 처방이 필요한 경우에는
자연스럽게 의료진 상담을 권장해 줘.
"""

def build_context(drug):
    return f"""
다음은 특정 의약품에 대한 공식 정보입니다.
이 정보는 참고용 컨텍스트입니다.

약 이름: {drug.name}
효능: {drug.effect or "정보 없음"}
복용 방법: {drug.usage or "정보 없음"}
주의사항: {drug.warning or "정보 없음"}
"""



def extract_reply_from_response(data):
    try:
        for item in data.get("output", []):
            if item.get("role") == "assistant":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        return c.get("text")
    except Exception as e:
        logger.error(f"❌ 응답 파싱 실패: {e}")
    return None



@api_view(["POST"])
@permission_classes([AllowAny])
def drug_chat(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    user_msg = request.data.get("message", "").strip()

    if not user_msg:
        return Response(
            {"reply": "질문을 입력해 주세요.\n※ 의료적 판단/처방이 아닌 정보 제공 목적입니다."},
            status=400
        )

    url = f"{settings.OPENAI_BASE_URL}/responses"

    payload = {
    "model": "gpt-5-nano",
    "instructions": SYSTEM_PROMPT,
    "input": f"""
    {build_context(drug)}

    사용자 질문:
    {user_msg}
    """.strip(),
        "reasoning": {"effort": "low"},
        
    }


    headers = {
        "Authorization": f"Bearer {settings.GMS_KEY}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, json=payload, headers=headers, timeout=30)

    if r.status_code != 200:
        logger.error(f"❌ OpenAI Error {r.status_code}: {r.text}")
        return Response(
            {"reply": "AI 응답 생성 실패\n※ 의료적 판단/처방이 아닌 정보 제공 목적입니다."},
            status=500
        )

    data = r.json()
    reply = extract_reply_from_response(data)

    if not reply:
        logger.error(f"❌ 빈 응답 수신: {json.dumps(data, ensure_ascii=False)}")
        reply = "답변을 생성하지 못했습니다."

    # ✅ 반드시 항상 Response 반환
    return Response({
        "reply": reply,
        "suggestions": ["효능", "복용법", "주의사항", "부작용"],
        "drug": {"id": drug.id, "name": drug.name},
    })



        

# ai 글 요약


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

# qr 코드

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