from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from .models import User, EmailOTP

import random


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, error_messages={'required': 'This field is required.'})
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False, required=True, error_messages={'required': 'This field is required.'}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            if not email:
                raise serializers.ValidationError({'email': 'Email is required.'}, code='authorization')
            if not password:
                raise serializers.ValidationError({'password': 'Password is required.'}, code='authorization')

        attrs['user'] = user
        return attrs

class SignUpSerializer(serializers.ModelSerializer):
    otp_code = serializers.CharField(required=True, error_messages={'required': 'This field is required.'})
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    is_finger_on = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('otp_code', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'password', 'is_finger_on', 'last_login', 'date_joined')
        extra_kwargs = {
            'password':{'write_only': True},
            'otp_code': {'required': True},
        }

    def validate(self, data):
        email_otp = EmailOTP.objects.filter(email=data['email']).first()

        if not email_otp:
            raise serializers.ValidationError("Invalid OTP")

        if email_otp.otp_code != data['otp_code']:
            raise serializers.ValidationError("Invalid OTP")
    
        user = User.objects.filter(email=data['email'])

        if user:
            raise serializers.ValidationError("User with this email already exists")
        
        user = User.objects.filter(username=data['username'])

        if user:
            raise serializers.ValidationError("User with this username already exists")

        return data

    def create(self, validated_data):
        validated_data.pop('otp_code')  # Remove 'otp_code' from validated data
        user = User.objects.create_user(**validated_data)
        return user


class GetUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'password', 'is_finger_on', 'last_login', 'date_joined')

class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def update_password(self, user, validated_data):
        current_password = validated_data['current_password']
        new_password = validated_data['new_password']

        if not user.check_password(current_password):
            raise serializers.ValidationError('Current password is incorrect')

        user.set_password(new_password)
        user.save()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)

class PasswordResetVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
    otp_code = serializers.CharField(required = True)