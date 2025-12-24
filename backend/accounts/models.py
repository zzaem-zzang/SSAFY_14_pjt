from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # username은 AbstractUser에 이미 있지만 override해서 제약조건 추가
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            MinLengthValidator(4, message="아이디는 최소 4자 이상이어야 합니다."),
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9]*$',
                message='아이디는 영문으로 시작하고 영문, 숫자만 사용 가능합니다.'
            )
        ],
        error_messages={
            'unique': '이미 사용 중인 아이디입니다.',
        },
        help_text='4~20자, 영문으로 시작, 영문/숫자만 가능'
    )
    
    nickname = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            MinLengthValidator(2, message="닉네임은 최소 2자 이상이어야 합니다."),
            RegexValidator(
                regex=r'^[가-힣a-zA-Z0-9]+$',
                message='닉네임은 한글, 영문, 숫자만 사용 가능합니다.'
            )
        ],
        error_messages={
            'unique': '이미 사용 중인 닉네임입니다.',
        },
        help_text='2~15자, 한글/영문/숫자만 가능'
    )

    def __str__(self):
        return self.nickname or self.username

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'