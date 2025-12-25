from dotenv import load_dotenv
import os
from pathlib import Path

# ========================
# Base & Env
# ========================

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(BASE_DIR / ".env")

# Django 시크릿 키 (환경변수 없으면 로컬 테스트용 기본값 사용)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-local-test-key')

# 외부 API 키들
E_DRUG_API_KEY = os.getenv('E_DRUG_API_KEY')
GMS_KEY = os.getenv("GMS_KEY")

# OpenAI 호환 API Base URL (SSAFY GMS 프록시)
OPENAI_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ========================
# Media
# 미디어 파일 설정
# ========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ========================
# Logging
# ========================
# 로그 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 로그 포맷 정의
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    # 콘솔 출력 핸들러
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    # 기본(root) 로거 설정
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
     # django 로거 설정
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 허용 호스트
# ========================
# Applications
# ========================
INSTALLED_APPS = [
    # Django 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 외부 라이브러리
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

     # 로컬 앱
    'accounts',
    'posts',
    'ingredients.apps.IngredientsConfig',
]

# 커스텀 User 모델 사용
AUTH_USER_MODEL = 'accounts.User'


# ========================
# Middleware
# ========================
MIDDLEWARE = [
    # CORS 처리
    'corsheaders.middleware.CorsMiddleware',

    # Django 기본 미들웨어
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 모든 Origin 허용
CORS_ALLOW_ALL_ORIGINS = True


# ========================
# URLs / WSGI
# ========================
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'


# ========================
# Templates
# ========================
# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ========================
# Database
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ========================
# Auth / Password
# ========================
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# Internationalization
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ========================
# Static
# ========================
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========================
# DRF
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
