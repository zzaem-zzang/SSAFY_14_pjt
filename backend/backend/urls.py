from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/comments/', include('posts.comments_urls')),
    path('api/', include('ingredients.urls')),
]
