from django.urls import path
from . import views

urlpatterns = [
    # 게시글
    path('', views.post_list_create, name='post-list-create'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),

    # 댓글
    path('<int:post_id>/comments/', views.comment_create, name='comment-create'),
    path('comments/<int:comment_id>/', views.comment_delete, name='comment-delete'),
]
