from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from .utils import send_activation_email
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            send_activation_email(user)

            return Response(
                {"message": "Registration successful. Please check your emails for activation."},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"error": "Please check your input and try again."},
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
