from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import CustomUser
from .serializers import RegistrationSerializer, PasswordConfirmSerializer
from .utils import send_activation_email, send_password_reset_email


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            send_activation_email(user)

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email
                    },
                    "token": str(refresh.access_token)
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"error": "Please check your input and try again.",
                "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ActivationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Activation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user is None:
            user = authenticate(username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            response = Response(
                {
                    "detail": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.email
                    }
                },
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                samesite='Lax'
            )

            return response

        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(
                {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
                status=status.HTTP_200_OK
            )

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            old_token = RefreshToken(refresh_token)
            user_id = old_token['user_id']
            user = CustomUser.objects.get(id=user_id)

            old_token.blacklist()
            new_token = RefreshToken.for_user(user)

            response = Response(
                {"detail": "Token refresh successful."},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key='access_token',
                value=str(new_token.access_token),
                httponly=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=str(new_token),
                httponly=True,
                samesite='Lax'
            )

            return response

        except (TokenError, ObjectDoesNotExist):
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )


class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if email:
            try:
                user = CustomUser.objects.get(email=email)
                send_password_reset_email(user)
            except ObjectDoesNotExist:
                pass

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
              
                user.set_password(serializer.validated_data['new_password'])
                user.save()

                return Response(
                    {"detail": "Your Password has been successfully reset."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Token is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
