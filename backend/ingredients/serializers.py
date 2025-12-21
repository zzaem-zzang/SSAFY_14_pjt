from rest_framework import serializers
from .models import Drug, Symptom, DrugComment
from accounts.serializers import UserSerializer
from django.db.models import Avg


from django.db.models import Avg



class DrugCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = DrugComment
        fields = ('id', 'content', 'rating', 'author', 'created_at')



class DrugSerializer(serializers.ModelSerializer):
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
            'avg_rating',
            'comments',
        )



class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name']



class DrugDetailSerializer(serializers.ModelSerializer):
    comments = DrugCommentSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        return obj.comments.aggregate(avg=Avg('rating'))['avg']

    class Meta:
        model = Drug
        fields = (
            'id', 'name', 'effect', 'usage', 'warning',
            'avg_rating', 'comments'
        )