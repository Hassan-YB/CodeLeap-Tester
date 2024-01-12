from rest_framework import permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from .models import User, EmailOTP
from .serializers import GetUserSerializer

import random

class IsAuthorized(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user is None:
            raise NotAuthenticated(detail="UnAuthorized User Action", code=None)

        return True
    
def generate_otp_code(length=6):
    """Generate a random OTP code of the specified length."""
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp

def verify_otp(user_email, otp):
    try:
        otp_obj = EmailOTP.objects.get(email=user_email)
    except EmailOTP.DoesNotExist:
        return False

    # if otp_obj.otp_code == otp and otp_obj.expired_at > timezone.now():
    #     # OTP is valid
    #     otp_obj.delete()  # Remove the OTP record from the database
    #     return True

    # Check the number of attempts
    max_attempts = 5
    if otp_obj.attempts >= max_attempts:
        # Exceeded maximum attempts
        otp_obj.delete()  # Remove the OTP record from the database
        return False

    # Increment the attempts count
    otp_obj.attempts += 1
    otp_obj.save()

    return False

def send_email_from_template(from_email, to_emails, subject, template_id, variables):

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject)


    message.template_id = template_id
    message.dynamic_template_data = variables
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"SendGrid API error: {str(e)}")


def generate_response_data(user):
    user_serializer = GetUserSerializer(user)
    refresh = RefreshToken.for_user(user)
    user_data = user_serializer.data
    user_data['refresh'] = str(refresh)
    user_data['access'] = str(refresh.access_token)
    first_name = user_data['first_name']
    #Dummy data
    user_data['is_logged_in'] = 1
    user_data['status'] = 1
    user_data['photo'] = None
    user_data['fcm'] = None
    user_data['balance'] = None
    user_data['bonus_balance'] = 0
    user_data['gcr'] = 100
    user_data['gpt'] = 0
    

    return {
        'success': f'Welcome {first_name}',
        'user': user_data,
    }