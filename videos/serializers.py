"""Serializers for serializing video entities and media attributes."""

from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize Video model data including absolute thumbnail URLs."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Meta configuration for VideoSerializer."""

        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        ]

    def get_thumbnail_url(self, obj):
        """Build and return absolute URL for thumbnail if available."""
        request = self.context.get('request')
        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
