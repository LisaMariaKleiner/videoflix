import os
import shutil
import subprocess
from django.conf import settings
from django.apps import apps


HLS_RESOLUTIONS = {
    '480p': 480,
    '720p': 720,
    '1080p': 1080,
}

HLS_BITRATES = {
    '480p': '1000k',
    '720p': '2500k',
    '1080p': '5000k',
}


def generate_thumbnail_for_video(video_id: int):
    """
    Generates a thumbnail image from the video at 5 seconds.
    Uses ffmpeg to extract a frame and Pillow to resize it.
    """
    Video = apps.get_model('video_app', 'Video')
    video = Video.objects.get(pk=video_id)

    if not video.video_file:
        print(f"[THUMBNAIL] Video {video.id} has no video_file")
        return

    input_path = video.video_file.path
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', f'thumb_{video.id}.jpg')
    
    # Ensure thumbnails directory exists
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

    # Extract frame at 5 seconds
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite if exists (must be before -i)
        '-ss', '5',  # Seek to 5 seconds
        '-i', input_path,
        '-vf', 'scale=320:180',  # Resize to thumbnail size
        '-vframes', '1',  # Extract only 1 frame
        '-q:v', '3',  # Quality (1-31, lower is better)
        thumbnail_path
    ]

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[THUMBNAIL] FFmpeg stderr for video {video.id}: {result.stderr}")
            return
        
        print(f"[THUMBNAIL] Generated thumbnail for video {video.id}: {thumbnail_path}")
        
        if os.path.exists(thumbnail_path):
            thumbnail_relative_path = f'thumbnails/thumb_{video.id}.jpg'
            Video.objects.filter(pk=video.id).update(thumbnail=thumbnail_relative_path)
            print(f"[THUMBNAIL] Thumbnail saved to database for video {video.id}")
        else:
            print(f"[THUMBNAIL] Thumbnail file not found after ffmpeg: {thumbnail_path}")
    
    except Exception as e:
        print(f"[THUMBNAIL] Exception for video {video.id}: {e}")


def generate_hls_for_video(video_id: int):
    """
    Runs in the background-worker (RQ). Fetches Video from DB and creates HLS files.
    Generates 480p, 720p, and 1080p versions with appropriate bitrates.
    """
    Video = apps.get_model('video_app', 'Video')
    video = Video.objects.get(pk=video_id)

    if not video.video_file:
        print(f"[HLS] Video {video.id} has no video_file")
        return

    input_path = video.video_file.path
    print(f"[HLS] Generating HLS for video {video.id}, Input: {input_path}")

    for resolution, height in HLS_RESOLUTIONS.items():
        output_dir = os.path.join(
            settings.MEDIA_ROOT, 'hls', str(video.id), resolution)
        os.makedirs(output_dir, exist_ok=True)
        output_playlist = os.path.join(output_dir, 'index.m3u8')
        segment_pattern = os.path.join(output_dir, 'segment_%03d.ts')

        video_bitrate = HLS_BITRATES.get(resolution, '2500k')

        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'h264',
            '-b:v', video_bitrate,
            '-c:a', 'aac',
            '-b:a', '128k',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            output_playlist,
        ]
        print(f"[HLS] Running ffmpeg for {video.id} {resolution}: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"[HLS] OK: {output_playlist}")
        except subprocess.CalledProcessError as e:
            print(f"[HLS] FFmpeg failed for video {video.id} {resolution}: {e}")


def delete_hls_for_video(video_id: int):
    """
    Deletes HLS directory for a video when the video is deleted.
    """
    hls_root = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    if os.path.isdir(hls_root):
        shutil.rmtree(hls_root)
        print(f"[HLS] HLS-Directory for video {video_id} deleted: {hls_root}")
