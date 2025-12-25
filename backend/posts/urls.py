from django.urls import path
from . import views

urlpatterns = [
    # ===== 게시글 =====

    # 게시글 목록 조회 / 게시글 생성
    path('', views.post_list_create, name='post-list-create'),

    # 게시글 상세 조회 / 수정 / 삭제
    path('<int:post_id>/', views.post_detail, name='post-detail'),

    # ===== 댓글 =====

    # 특정 게시글에 댓글 작성
    path('<int:post_id>/comments/', views.comment_create, name='comment-create'),

    # 댓글 삭제
    path('comments/<int:comment_id>/', views.comment_delete, name='comment-delete'),
]
