from django.urls import path
from . import views

urlpatterns = [
    path('drugs/save/', views.save_drug_by_name),
    path('drugs/<int:pk>/', views.drug_detail),
    path('drugs/<int:pk>/comments/', views.create_drug_comment),

    path('symptoms/', views.symptom_list),
    path('recommend/symptom/', views.recommend_by_symptom),
]

