"""Admin site configuration for video models."""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Video


@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    """Admin interface customization with import/export for Video model."""

    list_display = ('id', 'title', 'category', 'created_at')