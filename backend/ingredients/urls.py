from django.urls import path
from . import views

urlpatterns = [
    # --------------------
    # 기존 약 기능
    # --------------------
    path('drugs/', views.drug_list),
    path('drugs/save/', views.save_drug_by_name),
    path('drugs/<int:pk>/', views.drug_detail),
    path('drugs/<int:pk>/comments/', views.create_drug_comment),
    path('drugs/<int:drug_id>/reaction/', views.drug_reaction),

    # --------------------
    # 증상 관련
    # --------------------
    path('symptoms/', views.symptom_list),
    path('recommend/symptom/', views.recommend_by_symptom),

    # --------------------
    # ⭐ AI 기능 (여기 추가)
    # --------------------

    # urls.py

    path("drugs/<int:pk>/ai-summary/", views.drug_ai_summary),
    path("drugs/<int:pk>/ai-image/", views.drug_ai_image),
]

