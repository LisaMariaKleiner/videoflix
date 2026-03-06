from django.urls import path

from video_app.api.views import VideoListView, VideoHLSPlaylistView, VideoSegmentView

urlpatterns = [
    path('', VideoListView.as_view(), name='video-list'),
    path('<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSPlaylistView.as_view(), name='video-playlist'),
    path('<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video-segment'),
]
