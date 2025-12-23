from django.urls import path
from . import views

urlpatterns = [
    # --------------------
    # 기존 약 기능
    # --------------------
    path('drugs/', views.drug_list),
    path('drugs/<int:pk>/', views.drug_detail),
    path('drugs/<int:pk>/comments/', views.create_drug_comment),
    path('drugs/<int:drug_id>/reaction/', views.drug_reaction),
    path('drugs/popular/views/', views.popular_drugs_by_view),

    # --------------------
    # 증상 관련
    # --------------------
    path('drugs/ai-search/', views.drug_ai_search),
    
    # --------------------
    # ⭐ AI 기능 (여기 추가)
    # --------------------

    # urls.py
    

    path("drugs/<int:pk>/ai-summary/", views.drug_ai_summary),
    path("drugs/<int:pk>/ai-image/", views.drug_ai_image),
    
    # --------------------
    # ⭐ QR코드 관련 
    # --------------------
    
    path('drugs/<int:drug_id>/qr/', views.generate_drug_qr, name='drug-qr')
    
    
]

