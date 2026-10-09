from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'created_at',
            'category', 'thumbnail', 'video_file'
        ]