from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.http import HttpResponseRedirect
from django.conf import settings

from auth_app.api.serializers import RegistrationSerializer
from auth_app.utils import (
    decode_user_id,
    verify_activation_token,
    generate_activation_token,
    encode_user_id,
    get_user_by_id_and_verify_token,
    validate_password_match,
    reset_user_password,
)
from auth_app.tasks import queue_password_reset_email

User = get_user_model()

"""
This module defines API views for user registration, activation, login, logout, token refresh, and password reset.
"""
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'user': {
                        'id': user.id,
                        'email': user.email
                    },
                    'token': str(refresh.access_token)
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
            status=status.HTTP_400_BAD_REQUEST
        )

"""
The ActivateView handles the activation of a user's account. 
It takes a uidb64 and token as parameters, decodes the user ID, 
verifies the token, and if valid, activates the user's account. 
If any step fails, it returns an error response. Upon successful activation, 
it redirects the user to the login page of the frontend application.
"""
class ActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user_id = decode_user_id(uidb64)
        if user_id is None:
            return Response(
                {'error': 'Aktivierung fehlgeschlagen.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Aktivierung fehlgeschlagen.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verify_activation_token(user, token):
            return Response(
                {'error': 'Aktivierung fehlgeschlagen.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_email_verified = True
        user.is_active = True
        user.save()

        return HttpResponseRedirect(f"{settings.FRONTEND_BASE_URL}/pages/auth/login.html")

"""
The LoginView handles user authentication. 
It accepts email and password, authenticates the user, checks if the account is active, and if successful, 
returns a response with the user's information and JWT tokens.
"""
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is not activated.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        
        response = Response(
            {
                'detail': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.email,
                },
            },
            status=status.HTTP_200_OK
        )
        
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=settings.DEBUG == False,
            samesite='Lax',
            max_age=15 * 60,
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=settings.DEBUG == False,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
        )
        
        return response

"""
The LogoutView handles user logout by blacklisting the refresh token and 
deleting the access and refresh tokens from the client's cookies.
"""
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(
                {'error': 'Invalid refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        response = Response(
            {
                'detail': 'Logout successful! All tokens will be deleted. Refresh token is now invalid.'
            },
            status=status.HTTP_200_OK
        )
        response.delete_cookie('access_token', samesite='Lax')
        response.delete_cookie('refresh_token', samesite='Lax')

        return response

"""
The TokenRefreshView handles the refreshing of JWT access tokens.
It retrieves the refresh token from the client's cookies, validates it, and if valid, 
generates a new access token and returns it in the response. 
The new access token is also set in the client's cookies.
"""
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except Exception as e:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        response = Response(
            {
                'detail': 'Token refreshed',
                'access': access_token,
            },
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.DEBUG == False,
            samesite='Lax',
            max_age=15 * 60,
        )
        return response

"""The PasswordResetView handles the initiation of the password reset process."""
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'An email has been sent to reset your password.'},
                status=status.HTTP_200_OK
            )
        token = generate_activation_token(user)
        uidb64 = encode_user_id(user.id)
        queue_password_reset_email(user.id, token, uidb64)
        return Response(
            {'detail': 'An email has been sent to reset your password.'},
            status=status.HTTP_200_OK
        )

"""
The PasswordConfirmView handles the confirmation of the password reset process.
It takes a uidb64 and token as parameters, decodes the user ID, verifies the
token, and if valid, allows the user to set a new password.
"""
class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        user_id = decode_user_id(uidb64)
        user = get_user_by_id_and_verify_token(user_id, token)
        
        if user is None:
            return Response(
                {'error': 'Password reset failed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        is_valid, error_message = validate_password_match(new_password, confirm_password)
        if not is_valid:
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        reset_user_password(user, new_password)
        return Response(
            {'detail': 'Your Password has been successfully reset.'},
            status=status.HTTP_200_OK
        )

