from django.db import models
from core.models import BaseDateTimeModel

class Post(BaseDateTimeModel):
    username = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()