"""auth_views.py – Register, Login, Profile, Logout for all roles."""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.conf import settings

from api.models import User
from admin_panel.api.serializers.user_serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer
)


def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"{settings.SITE_URL}/api/v1/auth/verify-email/{uid}/{token}/"
    
    subject = "Verify your SmartSeller Account"
    message = f"Hi {user.name},\n\nPlease verify your email by clicking the link below:\n{link}\n\nAfter verification, an admin will review and approve your account."
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    return link


class RegisterView(APIView):
    """POST /api/v1/auth/register/ – Create a new user account."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Set unverified and unapproved
            user.is_email_verified = False
            user.is_approved = False
            user.save()
            
            try:
                link = send_verification_email(user)
                response_data = {
                    'message': 'Registration successful. Please check your email for verification.',
                    'user': UserProfileSerializer(user).data,
                    'verification_required': True
                }
                if settings.DEBUG:
                    response_data['debug_verification_link'] = link
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'message': 'Registration successful but failed to send email.',
                    'error': str(e),
                    'verification_required': True
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """GET /api/v1/auth/verify-email/<uidb64>/<token>/ – Verify user email."""
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            # Redirect to login page with success flag
            return redirect(f"{settings.SITE_URL}/login/?verified=true")
        
        # Redirect to login page with failure flag
        return redirect(f"{settings.SITE_URL}/login/?verified=false")


class LoginView(APIView):
    """POST /api/v1/auth/login/ – Authenticate and get JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user:
                if not user.is_email_verified:
                    return Response(
                        {'error': 'Email not verified. Please check your inbox.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if not user.is_approved:
                    return Response(
                        {'error': 'Account pending admin approval.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'message': 'Login successful.',
                        'user': UserProfileSerializer(user).data,
                        'tokens': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                    })
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """POST /api/v1/auth/logout/ – Blacklist refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/auth/profile/ – View and update own profile."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordView(APIView):
    """POST /api/v1/auth/forgot-password/ – Request a password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user:
            # In a real app, send email with reset link/token here
            return Response({'message': 'Reset link has been sent to your email.'})
        
        return Response({'message': 'Reset link has been sent to your email if the account exists.'})


class ResetPasswordView(APIView):
    """POST /api/v1/auth/reset-password/ – Complete password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('password')
        
        if not email or not new_password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'})
        
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
