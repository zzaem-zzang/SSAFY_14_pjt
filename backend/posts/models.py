from django.db import models
from django.conf import settings


class Post(models.Model):
    # 게시글 제목
    title = models.CharField(max_length=255)

    # 게시글 본문
    content = models.TextField()

    # 게시글 작성자
    # User 삭제 시 해당 사용자의 게시글도 함께 삭제
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    # 생성/수정 시각
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # 관리자/쉘에서 게시글을 제목으로 표시
        return self.title


class Comment(models.Model):
    # 어떤 게시글에 달린 댓글인지
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # 댓글 내용
    content = models.TextField()

    # 댓글 작성자
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # 댓글 작성 시각
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 댓글 식별용 문자열
        return f'Comment by {self.author} on {self.post.id}'
