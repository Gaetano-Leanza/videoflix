from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            # TODO: Hier fügen wir im nächsten Schritt den E-Mail-Versand ein
            return Response(
                {"message": "Registrierung erfolgreich. Bitte überprüfe deine E-Mails zur Aktivierung."}, 
                status=status.HTTP_201_CREATED
            )
            
        return Response(
            {"error": "Bitte überprüfe deine Eingaben und versuche es erneut."}, 
            status=status.HTTP_400_BAD_REQUEST
        )