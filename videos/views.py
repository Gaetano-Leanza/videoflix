from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Video
from .serializers import VideoSerializer
from .utils import get_hls_file_response


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all().order_by('-created_at')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        return get_hls_file_response(
            movie_id, resolution, 'index.m3u8', 'application/vnd.apple.mpegurl'
        )


class VideoSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        return get_hls_file_response(
            movie_id, resolution, segment, 'video/mp2t'
        )
