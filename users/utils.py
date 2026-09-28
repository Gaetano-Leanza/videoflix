from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_activation_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    activation_link = f"http://localhost:4200/activate/{uid}/{token}/"
    
    subject = 'Activate your Videoflix Account'
    message = f'Hello,\n\nPlease click on the following link to activate your account:\n{activation_link}\n\nYour Videoflix Team'
    
    send_mail(
        subject,
        message,
        'noreply@videoflix.com',
        [user.email],
        fail_silently=False,
    )