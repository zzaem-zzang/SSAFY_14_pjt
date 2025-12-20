from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_login(self):
        resp = self.client.post('/api/auth/register/', {'username': 't1', 'password': 'pw'})
        self.assertEqual(resp.status_code, 201)
        self.assertIn('token', resp.data)
        resp2 = self.client.post('/api/auth/login/', {'username': 't1', 'password': 'pw'})
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('token', resp2.data)

    def test_logout(self):
        self.client.post('/api/auth/register/', {'username': 't2', 'password': 'pw'})
        login = self.client.post('/api/auth/login/', {'username': 't2', 'password': 'pw'})
        token = login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 200)
