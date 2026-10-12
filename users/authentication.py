"""Custom authentication classes for cookie-based JWT authorization."""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using a JWT stored in HttpOnly cookies."""

    def authenticate(self, request):
        """Extract and validate the access token from request cookies."""
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
