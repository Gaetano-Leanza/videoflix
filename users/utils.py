from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import CustomUser


def send_activation_email(user):
    """Generate activation token and send activation link via email."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"http://localhost:4200/activate/{uid}/{token}/"
    subject = "Activate your Videoflix Account"
    msg = f"Hello,\n\nPlease activate your account:\n{link}\n\nVideoflix Team"
    send_mail(
        subject, msg, "noreply@videoflix.com", [user.email], fail_silently=False
    )


def send_password_reset_email(user):
    """Generate reset token and send password reset link via email."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"http://localhost:4200/reset-password/{uid}/{token}/"
    subject = "Reset your Videoflix Password"
    msg = f"Hello,\n\nPlease reset your password:\n{link}\n\nVideoflix Team"
    send_mail(
        subject, msg, "noreply@videoflix.com", [user.email], fail_silently=False
    )


def set_auth_cookies(response, refresh):
    """Attach JWT access and refresh tokens as secure HttpOnly cookies."""
    kwargs = {"httponly": True, "samesite": "Lax"}
    response.set_cookie("access_token", str(refresh.access_token), **kwargs)
    response.set_cookie("refresh_token", str(refresh), **kwargs)
    return response


def delete_auth_cookies(response):
    """Remove JWT authentication cookies from the HTTP response."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


def get_user_from_uidb64(uidb64):
    """Decode base64 encoded user ID and return corresponding user object."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        return None
