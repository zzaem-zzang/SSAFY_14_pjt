from django.urls import path
from . import views

urlpatterns = [
    path('drugs/save/', views.save_drug_by_name),
    path('drugs/<int:pk>/', views.drug_detail),

    path('symptoms/', views.symptom_list),
    path('recommend/symptom/', views.recommend_by_symptom),
]

