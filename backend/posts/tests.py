from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Post, Comment

User = get_user_model()


class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.post = Post.objects.create(title='Hello', content='World', author=self.user)

    def test_post_create(self):
        data = {'title': 'New', 'content': 'content'}
        resp = self.client.post(reverse('post-list'), data)
        self.assertEqual(resp.status_code, 201)

    def test_post_update_by_author(self):
        data = {'title': 'Updated', 'content': 'changed'}
        resp = self.client.put(reverse('post-detail', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(resp.status_code, 200)

    def test_post_update_by_other(self):
        other = User.objects.create_user(username='bob', password='pw')
        token = Token.objects.create(user=other)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        data = {'title': 'Bad', 'content': 'bad'}
        resp = self.client.put(reverse('post-detail', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(resp.status_code, 403)

    def test_comment_create_and_delete(self):
        # create comment
        resp = self.client.post(reverse('post-comments', kwargs={'post_id': self.post.pk}), {'content': 'hi'})
        self.assertEqual(resp.status_code, 201)
        comment_id = resp.data['id']
        # delete by author
        resp2 = self.client.delete(f'/api/comments/{comment_id}/')
        self.assertIn(resp2.status_code, (204, 200))

    def test_comment_delete_by_other(self):
        # alice creates a comment
        resp = self.client.post(reverse('post-comments', kwargs={'post_id': self.post.pk}), {'content': 'hi'})
        cid = resp.data['id']
        # bob attempts delete
        other = User.objects.create_user(username='charlie', password='pw')
        token = Token.objects.create(user=other)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp2 = self.client.delete(f'/api/comments/{cid}/')
        self.assertEqual(resp2.status_code, 403)

    def test_admin_can_delete_post(self):
        # create admin
        admin = User.objects.create_user(username='admin', password='pw', is_staff=True)
        token = Token.objects.create(user=admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.delete(reverse('post-detail', kwargs={'pk': self.post.pk}))
        self.assertIn(resp.status_code, (204, 200))
