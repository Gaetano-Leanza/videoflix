from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from .utils import send_activation_email  

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