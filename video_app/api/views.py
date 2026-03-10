import os
import mimetypes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, HttpResponse
from django.conf import settings

from video_app.models import Video
from video_app.api.serializers import VideoListSerializer
from .services import (
    HLS_RESOLUTIONS,
    is_valid_resolution,
    get_video_by_id,
    build_m3u8_path,
    read_and_rewrite_m3u8,
    is_valid_segment_name,
    build_segment_path,
    validate_segment_path,
)


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return list of all available videos."""
        videos = Video.objects.all()
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoHLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return HLS master playlist for a specific movie and resolution."""
        if not is_valid_resolution(resolution):
            return Response(
                {'detail': 'Resolution not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        video = get_video_by_id(movie_id)
        if video is None:
            return Response(
                {'detail': 'Video not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        m3u8_path = build_m3u8_path(movie_id, resolution)
        
        if not os.path.exists(m3u8_path):
            if not video.video_file:
                return Response(
                    {"detail": "No video file for this movie"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"detail": "HLS stream is still being generated."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        
        try:
            base_url = request.build_absolute_uri(
                f"/api/video/{video.id}/{resolution}/"
            )
            content = read_and_rewrite_m3u8(m3u8_path, base_url)
            
            response = HttpResponse(
                content,
                content_type='application/vnd.apple.mpegurl'
            )
            response['Content-Disposition'] = 'inline'
            return response
        except IOError:
            return Response(
                {'error': 'Error reading manifest file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return HLS video segment for a specific movie and resolution."""
        if not is_valid_resolution(resolution):
            return Response(
                {"detail": "Resolution not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not is_valid_segment_name(segment):
            return Response(
                {"detail": "Invalid segment name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        video = get_video_by_id(movie_id)
        if video is None:
            return Response(
                {'detail': 'Video not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        segment_path = build_segment_path(movie_id, resolution, segment)

        if not validate_segment_path(segment_path, movie_id, resolution):
            return Response(
                {'error': 'Invalid segment path.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not os.path.exists(segment_path):
            return Response(
                {'detail': 'Segment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            response = FileResponse(
                open(segment_path, 'rb'),
                content_type='video/MP2T'
            )
            response['Content-Disposition'] = 'inline'
            return response
        except IOError:
            return Response(
                {'error': 'Error reading segment file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
