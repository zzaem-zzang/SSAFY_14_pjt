from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'nickname',
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'nickname',
            'password',
            'password_confirm',
        )

    def validate_username(self, value):
        """
        아이디 유효성 검사:
        - 4~20자
        - 영문으로 시작
        - 영문, 숫자만 허용
        """
        if len(value) < 4:
            raise serializers.ValidationError('아이디는 최소 4자 이상이어야 합니다.')
        
        if len(value) > 20:
            raise serializers.ValidationError('아이디는 최대 20자까지 가능합니다.')
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', value):
            raise serializers.ValidationError('아이디는 영문으로 시작하고 영문, 숫자만 사용 가능합니다.')
        
        # 중복 체크
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('이미 사용 중인 아이디입니다.')
        
        return value

    def validate_nickname(self, value):
        """
        닉네임 유효성 검사:
        - 2~15자
        - 한글, 영문, 숫자만 허용
        """
        if len(value) < 2:
            raise serializers.ValidationError('닉네임은 최소 2자 이상이어야 합니다.')
        
        if len(value) > 15:
            raise serializers.ValidationError('닉네임은 최대 15자까지 가능합니다.')
        
        if not re.match(r'^[가-힣a-zA-Z0-9]+$', value):
            raise serializers.ValidationError('닉네임은 한글, 영문, 숫자만 사용 가능합니다.')
        
        # 중복 체크
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError('이미 사용 중인 닉네임입니다.')
        
        return value

    def validate_password(self, value):
        """
        비밀번호 유효성 검사:
        - 8자 이상
        - 영문, 숫자, 특수문자 포함
        """
        if len(value) < 8:
            raise serializers.ValidationError('비밀번호는 최소 8자 이상이어야 합니다.')
        
        # 영문 포함 확인
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError('비밀번호에 영문자가 포함되어야 합니다.')
        
        # 숫자 포함 확인
        if not re.search(r'\d', value):
            raise serializers.ValidationError('비밀번호에 숫자가 포함되어야 합니다.')
        
        # 특수문자 포함 확인
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError('비밀번호에 특수문자(!@#$%^&*등)가 포함되어야 합니다.')
        
        # Django 기본 password validation (선택사항)
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value

    def validate(self, data):
        """
        비밀번호 확인 일치 검증
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '비밀번호가 일치하지 않습니다.'
            })
        return data

    def create(self, validated_data):
        """
        유저 생성 (password_confirm 제거 후 저장)
        """
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
        )
        return user