from django.urls import path
from . import views

urlpatterns = [
    # ===== Auth =====
    path('register/', views.register),   # 회원가입
    path('login/', views.login),          # 로그인
    path('logout/', views.logout),        # 로그아웃

    # ===== User =====
    path('me/', views.user_info),         # 내 정보 조회
    path('withdraw/', views.withdraw),    # 회원탈퇴
]
