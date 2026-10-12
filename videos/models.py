"""Database models for video management and media assets."""

from django.db import models


class Video(models.Model):
    """Database model representing an uploaded video and its metadata."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100)
    thumbnail = models.ImageField(
        upload_to='thumbnails/', blank=True, null=True
    )
    video_file = models.FileField(upload_to='videos/')

    def __str__(self):
        """Return the string representation of the video instance."""
        return self.title
