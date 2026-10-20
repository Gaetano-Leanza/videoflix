"""API views for listing video catalog metadata and streaming HLS content."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer
from .utils import get_hls_file_response


class VideoListView(APIView):
    """Retrieve list of all available videos with serialized metadata."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch and return all video catalog entries ordered by creation date DESC."""
        videos = Video.objects.all().order_by('-created_at')
        serializer = VideoSerializer(
            videos, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoPlaylistView(APIView):
    """Serve HLS master/variant m3u8 playlist files for requested video."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return the m3u8 playlist stream file for given resolution."""
        return get_hls_file_response(
            movie_id, resolution, 'index.m3u8', 'application/vnd.apple.mpegurl'
        )


class VideoSegmentView(APIView):
    """Serve individual HLS video TS segment files for requested video."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return the binary TS transport stream video segment file."""
        return get_hls_file_response(
            movie_id, resolution, segment, 'video/MP2T'
        )
