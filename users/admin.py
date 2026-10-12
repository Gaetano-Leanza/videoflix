"""Admin site configuration for user models."""

from django.contrib import admin

from .models import CustomUser

admin.site.register(CustomUser)
