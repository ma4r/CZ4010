from django.db import models
from typing import Callable, Any
from django.contrib.auth import get_user_model
from json import JSONDecoder,JSONEncoder



class DataSetModel(models.Model):
    title = models.CharField(max_length=100,null=False)
    description = models.CharField(max_length=2000)
    data = models.JSONField(encoder = JSONEncoder, decoder=JSONDecoder)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    isPublic = models.BooleanField(default=False)
    times_used = models.PositiveIntegerField(default=0)





