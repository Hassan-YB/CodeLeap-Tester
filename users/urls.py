from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('logout/', UserLogoutView.as_view(), name='user_logout_view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', UserSignUpView.as_view(), name='user_signup'),
    path('send-email-otp/', EmailOTPView.as_view(), name='send_email_otp'),
    path('verify-email-otp/', VerifyOTPView.as_view(), name='verify_email_otp'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('check/username/', UsernameCheckView.as_view(), name='check-username'),
    path('check/email/', EmailCheckView.as_view(), name='check-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-verification/', PasswordResetVerificationView.as_view(), name='password_reset_verification'),
]
