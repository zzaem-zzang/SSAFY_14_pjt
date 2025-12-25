from rest_framework import serializers
from .models import Drug, DrugComment, DrugReaction
from accounts.serializers import UserSerializer
from django.db.models import Avg, Count


class DrugCommentSerializer(serializers.ModelSerializer):
    # 댓글 작성자 정보 (nickname 포함)
    author = UserSerializer(read_only=True)

    class Meta:
        model = DrugComment
        fields = (
            'id',
            'content',
            'rating',      # 사용자 별점 (선택)
            'author',      # ← author 안에 nickname 포함됨
            'created_at',
        )


class DrugSerializer(serializers.ModelSerializer):
    # 의약품 목록/요약 조회용 Serializer

    # 주석: 아래 필드들은 queryset에서 annotate로 계산된 값
    avg_rating = serializers.FloatField(read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    unhelpful_count = serializers.IntegerField(read_only=True)
    helpful_ratio = serializers.FloatField(read_only=True)

    # 의약품에 달린 댓글 목록
    comments = DrugCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Drug
        fields = (
            'id',
            'name',
            'image',
            'image_url',
            'avg_rating',
            'helpful_count',
            'unhelpful_count',
            'helpful_ratio',
            'comments',
            'effect',
            'usage',
            'warning',
        )


class DrugDetailSerializer(serializers.ModelSerializer):
    # 의약품 상세 조회용 Serializer

    comments = DrugCommentSerializer(many=True, read_only=True)

    # 댓글 별점 평균을 계산해서 반환
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        # 해당 의약품에 달린 댓글의 rating 평균
        return obj.comments.aggregate(avg=Avg('rating'))['avg']

    class Meta:
        model = Drug
        fields = (
            'id',
            'name',
            'effect',
            'usage',
            'warning',
            'image_url',
            'avg_rating',
            'comments',
            'view_count',
        )


class DrugReactionSerializer(serializers.ModelSerializer):
    # 의약품 반응(도움됨/도움안됨) Serializer
    class Meta:
        model = DrugReaction
        fields = ('id', 'reaction', 'created_at')
