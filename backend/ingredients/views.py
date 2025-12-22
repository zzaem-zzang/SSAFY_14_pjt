from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q, F, FloatField, ExpressionWrapper
import logging
from .models import Drug, Symptom, DrugReaction
from .utils import fetch_drug_from_api
from .serializers import DrugSerializer,SymptomSerializer, DrugCommentSerializer, DrugReactionSerializer, DrugDetailSerializer

logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_drug_comment(request, pk):
    drug = get_object_or_404(Drug, pk=pk)

    serializer = DrugCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        author=request.user,
        drug=drug
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([AllowAny])
def save_drug_by_name(request):
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
        # 로그에 상세 정보 남김
        logger.exception('외부 API 호출 중 예외 발생')
        err = str(e)
        # 인증 관련 에러인 경우(401) 보다 명확한 메시지 반환
        if '401' in err or 'Unauthorized' in err or '인증' in err:
            return Response({'error': '외부 API 인증 실패: E_DRUG_API_KEY를 확인하세요.'}, status=502)
        return Response({'error': f'외부 API 호출 실패: {err}'}, status=502)
    
    body = data.get('body', {})
    items = body.get('items', [])

   
    if isinstance(items, dict):
        items = items.get('item', [])

    # 결과가 아예 없을 때도 성공 처리
    if not items:
        return Response(
            {
                'message': '검색 결과가 없습니다.',
                'saved_count': 0
            },
            status=200
        )

    saved = []
    failed = []

    #  하나라도 있으면 무조건 성공
    for item in items:
        try:
            item_name = item.get('itemName')
            if not item_name:
                continue

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
            # 👉 개별 실패는 전체 실패 아님
            failed.append(str(e))

    return Response(
        {
            'saved_count': len(saved),
            'saved': saved,
            'failed_count': len(failed),
            'image_url': drug.image_url,
        },
        status=200
    )



# Drug를 상세 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def drug_detail(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    serializer = DrugDetailSerializer(drug)  # ⭐ 핵심
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_by_symptom(request):
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

@api_view(['GET'])
@permission_classes([AllowAny])
def symptom_list(request):
    symptoms = Symptom.objects.all()
    serializer = SymptomSerializer(symptoms, many=True)
    return Response(serializer.data)




@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def drug_reaction(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)

    # ----------------------
    # GET: 반응 개수 + 내 반응
    # ----------------------
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

        # ⭐ 로그인한 경우에만 내 반응 조회
        if request.user.is_authenticated:
            my = DrugReaction.objects.filter(
                user=request.user,
                drug=drug
            ).first()
            data['my_reaction'] = my.reaction if my else None

        return Response(data, status=status.HTTP_200_OK)

    # ----------------------
    # POST: 로그인 필수
    # ----------------------
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
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def drug_list(request):
    """
    약 목록 조회 + 정렬 + 사용자 반응 비율
    정렬 옵션:
    - 기본순   : order 없음
    - 도움순   : order=helpful
    - 평점순   : order=rating
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
    )

    # ⭐ 도움됐어요 비율 (%)
    drugs = drugs.annotate(
        helpful_ratio=ExpressionWrapper(
            100.0 * F('helpful_count') /
            (F('helpful_count') + F('unhelpful_count')),
            output_field=FloatField()
        )
    )

    # 정렬
    if order == 'helpful':
        drugs = drugs.order_by('-helpful_ratio')
    elif order == 'rating':
        drugs = drugs.order_by('-avg_rating')
    else:
        drugs = drugs.order_by('-id')

    serializer = DrugSerializer(drugs, many=True)
    return Response(serializer.data)
