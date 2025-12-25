from rest_framework import serializers
from django.contrib.auth import get_user_model

# settings.AUTH_USER_MODEL 에 등록된 User 모델을 가져옴
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    유저 정보 조회용 Serializer
    - 외부로 노출해도 되는 최소 필드만 포함
    """

    class Meta:
        model = User
        fields = (
            'id',        # 유저 고유 ID
            'username',  # 로그인용 아이디
            'nickname',  # 서비스 내 표시 이름
        )


class RegisterSerializer(serializers.ModelSerializer):
    """
    회원가입용 Serializer
    - 비밀번호 2회 입력 검증
    - 닉네임 중복 검증
    """

    # 비밀번호는 응답에 포함되지 않도록 write_only 설정
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    # 비밀번호 확인용 필드 (DB에는 저장되지 않음)
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

    #  비밀번호 2번 입력 검증
    def validate(self, data):
        # password 와 password_confirm 값이 다르면 에러 발생
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '비밀번호가 일치하지 않습니다.'
            })
        return data

    #  닉네임 중복 검증
    def validate_nickname(self, value):
        # 동일한 닉네임이 이미 존재하는지 확인
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError('이미 사용 중인 닉네임입니다.')
        return value

    #  실제 유저 생성
    def create(self, validated_data):
        # DB에 저장하지 않는 password_confirm 제거
        validated_data.pop('password_confirm')

        # Django 기본 create_user 사용 (비밀번호 해싱 포함)
        user = User.objects.create_user(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
        )
        return user
