from rest_framework import serializers
from .models import Drug, DrugComment, DrugReaction
from accounts.serializers import UserSerializer
from django.db.models import Avg, Count

class DrugCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = DrugComment
        fields = (
            'id',
            'content',
            'rating',
            'author',      # ← author 안에 nickname 포함됨
            'created_at',
        )


class DrugSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    helpful_count = serializers.IntegerField(read_only=True)
    unhelpful_count = serializers.IntegerField(read_only=True)
    helpful_ratio = serializers.FloatField(read_only=True)
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
            'warning'
        )





class DrugDetailSerializer(serializers.ModelSerializer):
    comments = DrugCommentSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
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
    class Meta:
        model = DrugReaction
        fields = ('id', 'reaction', 'created_at')
