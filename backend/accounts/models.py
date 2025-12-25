from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    기본 Django User 모델을 확장한 커스텀 유저 모델
    - username 기반 인증 유지
    - 서비스용 표시 이름으로 nickname 추가
    """

    nickname = models.CharField(
        max_length=30,
        unique=True,
    )

    def __str__(self):
        return self.nickname if self.nickname else self.username
