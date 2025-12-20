from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

from .models import Drug, Symptom
from .utils import fetch_drug_from_api
from .serializers import DrugSerializer,SymptomSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
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
                }
            )

            saved.append({
                'id': drug.id,
                'name': drug.name,
                'created': created,
            })

        except Exception as e:
            # 👉 개별 실패는 전체 실패 아님
            failed.append(str(e))

    return Response(
        {
            'saved_count': len(saved),
            'saved': saved,
            'failed_count': len(failed),
        },
        status=200
    )



# Drug를 상세 조회
@api_view(['GET'])
def drug_detail(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    serializer = DrugSerializer(drug)
    return Response(serializer.data)

@api_view(['GET'])
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
def symptom_list(request):
    symptoms = Symptom.objects.all()
    serializer = SymptomSerializer(symptoms, many=True)
    return Response(serializer.data)