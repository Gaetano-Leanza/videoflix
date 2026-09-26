from rest_framework import serializers
from .models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']
        
      
        if password != repeated_password:
            raise serializers.ValidationError({'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'})
        
       
        user = CustomUser(
            email=self.validated_data['email'],
            username=self.validated_data['email'] 
        )
        user.set_password(password)
        user.is_active = False 
        user.save()
        
        return user