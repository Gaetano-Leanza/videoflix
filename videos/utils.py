"""Utility helper functions for resolving and serving video stream assets."""

import os

from django.http import FileResponse, Http404

from .models import Video


def get_hls_file_response(movie_id, resolution, filename, content_type):
    """Retrieve requested HLS file and return it as a streaming FileResponse."""
    video = Video.objects.filter(id=movie_id).first()
    if not video or not video.video_file:
        raise Http404("Video nicht gefunden")
    base_dir = os.path.dirname(video.video_file.path)
    file_path = os.path.join(base_dir, str(video.id), resolution, filename)
    if not os.path.exists(file_path):
        raise Http404("Datei nicht gefunden")
    return FileResponse(open(file_path, 'rb'), content_type=content_type)
