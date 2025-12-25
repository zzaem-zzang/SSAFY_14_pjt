from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

# 커스텀 User 모델 가져오기
User = get_user_model()


class AuthTests(APITestCase):
    """
    인증 관련 API 테스트
    - 회원가입
    - 로그인
    - 로그아웃
    """

    def test_register_and_login(self):
        # 회원가입 요청
        resp = self.client.post(
            '/api/auth/register/',
            {
                'username': 't1',
                'password': 'pw',
            }
        )

        # 회원가입 성공 여부 확인
        self.assertEqual(resp.status_code, 201)
        self.assertIn('token', resp.data)

        # 로그인 요청
        resp2 = self.client.post(
            '/api/auth/login/',
            {
                'username': 't1',
                'password': 'pw',
            }
        )

        # 로그인 성공 여부 확인
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('token', resp2.data)

    def test_logout(self):
        # 회원가입
        self.client.post(
            '/api/auth/register/',
            {
                'username': 't2',
                'password': 'pw',
            }
        )

        # 로그인 후 토큰 획득
        login = self.client.post(
            '/api/auth/login/',
            {
                'username': 't2',
                'password': 'pw',
            }
        )
        token = login.data['token']

        # 인증 헤더에 토큰 설정
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # 로그아웃 요청 및 성공 여부 확인
        self.assertEqual(
            self.client.post('/api/auth/logout/').status_code,
            200
        )
