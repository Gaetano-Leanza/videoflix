from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import CustomUser
from .serializers import RegistrationSerializer, PasswordConfirmSerializer
from .utils import (
    send_activation_email, send_password_reset_email,
    set_auth_cookies, delete_auth_cookies, get_user_from_uidb64
)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Bitte Eingaben prüfen.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        send_activation_email(user)
        token = default_token_generator.make_token(user)
        return Response(
            {"user": {"id": user.id, "email": user.email}, "token": token},
            status=status.HTTP_201_CREATED
        )


class ActivationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = get_user_from_uidb64(uidb64)
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Activation link is invalid or has expired."},
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email, password = request.data.get(
            'email'), request.data.get('password')
        user = authenticate(username=email, password=password)
        if not user or not user.is_active:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        data = {"detail": "Login successful", "user": {
            "id": user.id, "username": user.email}}
        return set_auth_cookies(Response(data), RefreshToken.for_user(user))


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
            msg = "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            return delete_auth_cookies(Response({"detail": msg}, status=status.HTTP_200_OK))
        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.COOKIES.get('refresh_token')
        if not token_str:
            return Response({"error": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(token_str)
            user = CustomUser.objects.get(id=token['user_id'])
            new_refresh = RefreshToken.for_user(user)
            token.blacklist()
            data = {"detail": "Token refreshed",
                    "access": str(new_refresh.access_token)}
            return set_auth_cookies(Response(data, status=status.HTTP_200_OK), new_refresh)
        except Exception:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            send_password_reset_email(user)
        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        user = get_user_from_uidb64(uidb64)
        pw, confirm_pw = request.data.get(
            'new_password'), request.data.get('confirm_password')
        if not user or not default_token_generator.check_token(user, token):
            return Response({"error": "Reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if not pw or pw != confirm_pw:
            return Response({"error": "Passwords do not match or are empty."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(pw)
        user.save()
        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)
