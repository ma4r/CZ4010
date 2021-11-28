from .models import DataSetModel
from rest_framework import serializers
from django.core import exceptions



class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSetModel
        exclude = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super(DataSerializer, self).create(validated_data)
