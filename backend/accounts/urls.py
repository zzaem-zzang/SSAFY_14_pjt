from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('me/', views.user_info),
    path('withdraw/', views.withdraw),  # ⭐ 회원탈퇴
]
