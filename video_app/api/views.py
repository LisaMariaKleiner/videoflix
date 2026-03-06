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
from .services import HLS_RESOLUTIONS


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
        if resolution not in HLS_RESOLUTIONS:
            return Response({'detail': 'Resolution not found'}, status=404)

        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            return Response(
                {'detail': 'Video not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        m3u8_path = os.path.join(
            settings.MEDIA_ROOT,
            'hls',
            str(movie_id),
            resolution,
            'index.m3u8'
        )

        if not os.path.exists(m3u8_path):
            if not video.video_file:
                return Response(
                    {"detail": "No video file for this movie"},
                    status=404,
                )
            return Response(
                {"detail": "HLS stream is still being generated."},
                status=503,
            )

        try:
            with open(m3u8_path, 'r') as f:
                content = f.read()

            lines = content.splitlines()
            new_lines = []
            base_url = request.build_absolute_uri(
                f"/api/video/{video.id}/{resolution}/")

            for line in lines:
                if line.startswith('#') or not line.strip():
                    new_lines.append(line)
                else:
                    new_lines.append(base_url + line.strip())
            rewritten_content = '\n'.join(new_lines) + '\n'

            response = HttpResponse(rewritten_content, content_type='application/vnd.apple.mpegurl')
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
        if resolution not in HLS_RESOLUTIONS:
            return Response({"detail": "Resolution not found."}, status=404)

        if "/" in segment or ".." in segment:
            return Response({"detail": "Invalid segment name"}, status=404)

        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            return Response(
                {'detail': 'Video not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            'hls',
            str(movie_id),
            resolution,
            segment
        )

        real_path = os.path.realpath(segment_path)
        media_hls_path = os.path.realpath(
            os.path.join(settings.MEDIA_ROOT, 'hls', str(movie_id), resolution)
        )

        if not real_path.startswith(media_hls_path):
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
            response = FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
            response['Content-Disposition'] = 'inline'
            return response
        except IOError:
            return Response(
                {'error': 'Error reading segment file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
