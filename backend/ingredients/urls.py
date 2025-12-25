from django.urls import path
from . import views

urlpatterns = [
    # --------------------
    # 약 기능
    # --------------------

    # 의약품 목록 조회
    path('drugs/', views.drug_list),

    # 의약품 상세 조회
    path('drugs/<int:pk>/', views.drug_detail),

    # 의약품 댓글 작성
    path('drugs/<int:pk>/comments/', views.create_drug_comment),

    # 의약품 반응 (도움됨 / 도움안됨)
    path('drugs/<int:drug_id>/reaction/', views.drug_reaction),

    # 조회수 기준 인기 의약품
    path('drugs/popular/views/', views.popular_drugs_by_view),


    # --------------------
    # 증상 관련
    # --------------------

    # AI 기반 증상 → 의약품 검색
    path('drugs/ai-search/', views.drug_ai_search),


    # --------------------
    #  AI 기능
    # --------------------

    # AI 요약 정보 조회
    path('drugs/<int:pk>/ai-summary/', views.drug_ai_summary),

    # 의약품 전용 챗봇
    path('drugs/<int:pk>/chat/', views.drug_chat, name='drug_chat'),


    # --------------------
    #  QR 코드 관련
    # --------------------

    # 의약품 정보 QR 코드 생성
    path('drugs/<int:drug_id>/qr/', views.generate_drug_qr, name='drug-qr'),
]
