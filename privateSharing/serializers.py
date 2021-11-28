from dataSet.models import DataSetModel
from .models import PrivateSharingModel
from rest_framework import serializers
from django.core import exceptions
from json import JSONEncoder,JSONDecoder


class CreatePrivateSharingSerializer(serializers.ModelSerializer):
    session_id = serializers.SerializerMethodField("get_id")

    class Meta:
        model = PrivateSharingModel
        fields = ['data','session_id','client1']

    def create(self, validated_data):
        validated_data["client1"] = self.context['request'].user
        print(validated_data['client1'])
        return super(CreatePrivateSharingSerializer,self).create(validated_data)
    def get_id(self,obj):
        return obj.id

class UpdateSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrivateSharingModel
        fields = ['enc_data','client2','status']




class PrivateSharingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateSharingModel
        fields = '__all__'