"""Serializers for user registration and authentication workflows."""

from rest_framework import serializers

from .models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize and validate registration data for new user accounts."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Ensure password and confirmed_password match."""
        if attrs.get('password') != attrs.get('confirmed_password'):
            raise serializers.ValidationError(
                {'error': 'Please check your input and try again.'}
            )
        return attrs

    def create(self, validated_data):
        """Create and return a new inactive CustomUser instance."""
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['email'],
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate confirmation data for resetting user passwords."""

    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        """Validate that both password fields match identically."""
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {'detail': 'The entered passwords do not match.'}
            )
        return attrs
