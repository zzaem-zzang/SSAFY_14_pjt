from rest_framework import serializers
from .models import Drug, Symptom


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = '__all__'


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name']
