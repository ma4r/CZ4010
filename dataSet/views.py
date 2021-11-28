from rest_framework import viewsets, status,authentication
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.request import Request

from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DataSetModel
from .serializers import DataSerializer
# Create your views here.

class DataViewSet(viewsets.ModelViewSet,LoginRequiredMixin):
    http_method_names = ['get', 'post','delete','patch']
    serializer_class = DataSerializer
    def get_queryset(self):
        return DataSetModel.objects.filter(user=self.request.user)


