"""Database models for custom user management."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser with unique email."""

    email = models.EmailField(unique=True)

    def __str__(self):
        """Return the string representation of the user."""
        return self.username
