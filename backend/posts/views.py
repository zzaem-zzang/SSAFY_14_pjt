from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer
from .permissions import IsAuthorOrAdmin


# ========================
# 게시글 목록 / 생성
# ========================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_create(request):
    # 게시글 목록 조회
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    # 게시글 생성 (로그인 필요)
    if request.method == 'POST':
        serializer = PostDetailSerializer(data=request.data)
        if serializer.is_valid():
            # 작성자는 요청한 사용자로 설정
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================
# 게시글 상세 / 수정 / 삭제
# ========================
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, post_id):
    # 게시글 조회 (없으면 404)
    post = get_object_or_404(Post, pk=post_id)

    # 게시글 상세 조회
    if request.method == 'GET':
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    # 수정 / 삭제는 작성자만 가능
    if post.author != request.user:
        return Response(
            {'detail': '권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # 게시글 수정
    if request.method == 'PUT':
        serializer = PostDetailSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시글 삭제
    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========================
# 댓글 생성
# ========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, post_id):
    # 댓글이 달릴 게시글 조회
    post = get_object_or_404(Post, pk=post_id)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        # 댓글 작성자와 게시글을 서버에서 주입
        serializer.save(
            author=request.user,
            post=post
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================
# 댓글 삭제
# ========================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_id):
    # 댓글 조회
    comment = get_object_or_404(Comment, pk=comment_id)

    # 댓글 작성자만 삭제 가능
    if comment.author != request.user:
        return Response(
            {'detail': '작성자만 댓글을 삭제할 수 있습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
