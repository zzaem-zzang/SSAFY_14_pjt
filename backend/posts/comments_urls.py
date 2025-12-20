from django.urls import path
from .views import CommentDestroyAPIView

urlpatterns = [
    path('<int:pk>/', CommentDestroyAPIView.as_view(), name='comment-delete'),
]
