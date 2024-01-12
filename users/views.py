from rest_framework import viewsets, generics, permissions, mixins
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.contrib.auth import get_user_model, logout
from datetime import timedelta

from .serializers import *
from .models import User, EmailOTP
from .utils import send_email_from_template, generate_otp_code, generate_response_data

import requests
import threading
import time


class UserLoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        response_data = generate_response_data(user)
        
        return Response(response_data)
    
class UserLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

class UserSignUpView(GenericAPIView):
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = generate_response_data(user)
        
        return Response(response_data)

class EmailOTPView(APIView):

    def post(self, request, format=None):
        email = request.data.get('email')

        if email:
            existing_otp = EmailOTP.objects.filter(email=email).first()

            # if existing_otp:
            #     if existing_otp.is_verified:
            #         return Response({'error': 'Email already verified'}, status=400)
            #     elif existing_otp.is_verified is False:
            #         return Response({'error': 'OTP already sent for this email.'}, status=400)

            otp_code = generate_otp_code()
            user_otp, created = EmailOTP.objects.get_or_create(email = email)
            user_otp.otp_code = otp_code
            user_otp.save()

            body = {"otp": otp_code}
            t = threading.Thread(
                target=send_email_from_template,
                args=(
                settings.EMAIL_HOST_USER, [email],
                "Account Registration: Verify Email",
                settings.EMAIL_OTP_TEMPLATE_ID, body),
                daemon=True)
            t.start()
            return Response({'message': 'OTP sent successfully.'})
        else:
            return Response({'error': 'Email is required.'}, status=400)
        
class VerifyOTPView(APIView):

    def post(self, request, format=None):
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        if email and otp_code:
            try:
                otp = EmailOTP.objects.get(email=email)
            except EmailOTP.DoesNotExist:
                return Response({'error': 'Invalid OTP or email.'}, status=400)

            if otp.otp_code == otp_code and not otp.is_verified:
                if otp.attempts >= 5:
                    otp.delete()
                    return Response({'error': 'OTP attempts exceeded.'}, status=400)

                otp.is_verified = True
                otp.save()

                return Response({'message': 'OTP verification successful.'})
            else:
                otp.attempts += 1
                otp.save()

                return Response({'error': 'Invalid OTP or email.'}, status=400)
        else:
            return Response({'error': 'Email and OTP are required.'}, status=400)
        
class UsernameCheckView(APIView):

    def post(self, request):
        username = request.data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                return Response({'message': 'Username is taken'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'message': 'Username is available'}, status=200)
        else:
            return Response({'error': 'Username is required.'}, status=400)

class EmailCheckView(APIView):

    def post(self, request):
        email = request.data.get('email')

        if email:
            if User.objects.filter(email=email).exists():
                return Response({'message': 'Email is taken'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'message': 'Email is available'}, status=200)
        else:
            return Response({'error': 'Email is required.'}, status=400)      


class UpdatePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        serializer.update_password(user, serializer.validated_data)

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
    
class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if email:
            existing_otp = EmailOTP.objects.filter(email=email).first()
            cooldown_duration = timedelta(minutes=1)  # Set the cooldown period to 1 minute

            if existing_otp and existing_otp.updated_at:
                # Check if the cooldown period has not passed yet
                cooldown_expired = timezone.now() - existing_otp.updated_at > cooldown_duration
                if not cooldown_expired:
                    time_left = (existing_otp.updated_at + cooldown_duration) - timezone.now()
                    return Response({
                        'error': f'Please wait {time_left.seconds} seconds before sending another reset request.'
                    }, status=429)

            otp_code = generate_otp_code()
            user_otp, created = EmailOTP.objects.get_or_create(email=email)
            user_otp.otp_code = otp_code
            user_otp.updated_at = timezone.now()  # Update the updated_at field
            user_otp.save()

            body = {"otp": otp_code}
            t = threading.Thread(
                target=send_email_from_template,
                args=(
                settings.EMAIL_HOST_USER, [email],
                "eLoad Account: Reset Account PIN",
                settings.PASSWORD_RESET_TEMPLATE_ID, body),
                daemon=True)
            t.start()
            return Response({'message': 'OTP sent successfully.'})

        return Response({'success': True})
    

class PasswordResetVerificationView(APIView):
    serializer_class = PasswordResetVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=404)

        email_otp = EmailOTP.objects.filter(email=email).first()

        if not email_otp or email_otp.otp_code != otp_code:
            return Response({"error": "Invalid OTP code."}, status=400)

        # Reset the user's password
        user.set_password(password)
        user.save()

        # Optionally, you may choose to delete the email_otp record here

        return Response({"message": "Password reset successful."}, status=200)