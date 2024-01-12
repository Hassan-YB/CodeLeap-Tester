from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseDateTimeModel


class User(AbstractUser):
    phone_number = models.CharField(max_length=25, blank=True)
    is_finger_on = models.BooleanField(default=False)


class EmailOTP(BaseDateTimeModel):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Email OTP"

    def __str__(self):
        return f"{self.email} -> {self.otp_code} -> {self.is_verified}"
