from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ===== Admin =====
    path('admin/', admin.site.urls),

    # ===== API =====
    path('api/auth/', include('accounts.urls')),     # 인증
    path('api/posts/', include('posts.urls')),       # 게시글
    path('api/', include('ingredients.urls')),       # 의약품 / 성분
]

# ===== Media (개발 환경) =====
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
