from django.db import models

class BaseDateTimeModel(models.Model):
    created_datetime = models.DateTimeField(auto_now_add = True)
    updated_datetime = models.DateTimeField(auto_now = True)

