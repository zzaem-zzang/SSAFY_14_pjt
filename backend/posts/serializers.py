from rest_framework import serializers
from .models import Post, Comment
from accounts.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """댓글 Serializer"""

    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'content', 'author', 'created_at')
        read_only_fields = ('id', 'author', 'created_at', 'post')


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록용 Serializer"""

    author = UserSerializer(read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'excerpt', 'created_at')

    def get_excerpt(self, obj):
        return obj.content[:200]


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 Serializer"""

    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'author',
            'comments',
            'created_at',
            'updated_at',
        )
