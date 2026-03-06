from rest_framework import serializers
from video_app.models import Video


class VideoListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        """
        Generates the full thumbnail URL. Returns a placeholder if no thumbnail is uploaded.
        """
        PLACEHOLDER_IMAGE = 'https://via.placeholder.com/300x200?text=No+Thumbnail'
        
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            url = obj.thumbnail.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        
        return PLACEHOLDER_IMAGE
