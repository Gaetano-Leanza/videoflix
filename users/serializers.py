from rest_framework import serializers
from .models import CustomUser
# Zeile 3 (doppelter Import) gelöscht

class RegistrationSerializer(serializers.ModelSerializer):
    
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # WICHTIG: Hier muss eingerückt werden!
    def save(self):
        password = self.validated_data['password']
        confirmed_password = self.validated_data['confirmed_password']

        if password != confirmed_password:
            raise serializers.ValidationError(
                {'error': 'Please check your input and try again.'})
        
        user = CustomUser(
            email=self.validated_data['email'],
            username=self.validated_data['email']
        )
        user.set_password(password)
        user.is_active = False
        user.save()

        return user


class PasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {"detail": "Die Passwörter stimmen nicht überein."})
        return attrs
