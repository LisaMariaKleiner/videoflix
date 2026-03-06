from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os

from .models import Video
from .api.services import delete_hls_for_video, generate_thumbnail_for_video, generate_hls_for_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created, **kwargs):
    """
    Automatically executed when a video is uploaded.
    1. First generates thumbnail from video frame
    2. Then queues HLS job for background processing.
    Only works in Docker environments with RQ available.
    """
    if instance.video_file and not os.environ.get('WINDOWS_SKIP_RQ'):
        try:
            print(f"[SIGNAL] Generating thumbnail for video {instance.id}")
            generate_thumbnail_for_video(instance.id)
            
            from django_rq import get_queue
            print(f"[SIGNAL] post_save for video {instance.id}, enqueue HLS job")
            queue = get_queue("default")
            queue.enqueue(generate_hls_for_video, instance.id)
        except (ImportError, ValueError) as e:
            print(f"[SIGNAL] RQ not available: {e}")
            try:
                print(f"[SIGNAL] Generating thumbnail locally")
                generate_thumbnail_for_video(instance.id)
                print(f"[SIGNAL] Generating HLS locally")
                generate_hls_for_video(instance.id)
            except Exception as e:
                print(f"[SIGNAL] Error in local generation: {e}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs):
    """
    Automatically executed when a video is deleted.
    The HLS directory will be deleted too.
    """
    print(f"[SIGNAL] post_delete for video {instance.id}, deleting HLS-Files.")
    delete_hls_for_video(instance.id)
