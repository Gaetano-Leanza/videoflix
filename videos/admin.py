"""Admin site configuration for video models."""

from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin interface customization for Video model."""

    list_display = ('id', 'title', 'category', 'created_at')