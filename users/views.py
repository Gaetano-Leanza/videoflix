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
                {"error": "Bitte überprüfe deine Eingaben und versuche es erneut."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        send_activation_email(user)
        return Response(
            {"message": "Registrierung erfolgreich. Bitte prüfe deine E-Mails."},
            status=status.HTTP_201_CREATED
        )


class ActivationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = get_user_from_uidb64(uidb64)
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account aktiviert."}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Aktivierungslink ungültig oder abgelaufen."},
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
                {"error": "Ungültige Anmeldedaten oder Account nicht aktiv."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        res = Response({"detail": "Login erfolgreich", "user": {
                       "id": user.id, "email": user.email}})
        return set_auth_cookies(res, RefreshToken.for_user(user))


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
            return delete_auth_cookies(Response({"detail": "Erfolgreich abgemeldet."}))
        except TokenError:
            return Response({"error": "Ungültiger Token."}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(APIView):
    def post(self, request):
        token_str = request.COOKIES.get('refresh_token')
        if not token_str:
            return Response({"error": "Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(token_str)
            user = CustomUser.objects.get(id=token['user_id'])
            token.blacklist()
            return set_auth_cookies(Response({"detail": "Token erneuert."}), RefreshToken.for_user(user))
        except Exception:
            return Response({"error": "Ungültiger Token."}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if email:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                send_password_reset_email(user)
        return Response(
            {"detail": "Falls die E-Mail existiert, wurde ein Link gesendet."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = get_user_from_uidb64(uidb64)
        if user and default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Passwort geändert."}, status=status.HTTP_200_OK)
        return Response({"error": "Link ungültig."}, status=status.HTTP_400_BAD_REQUEST)
