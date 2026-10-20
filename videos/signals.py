"""Signal handlers for reacting to video model lifecycle events."""

import os
import shutil
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import django_rq

from .models import Video
from .tasks import convert_video_to_hls


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Trigger asynchronous HLS transcoding when a new video is uploaded."""
    if created and instance.video_file:
        django_rq.enqueue(convert_video_to_hls, instance.id)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Delete original video file and converted HLS folder upon deletion."""
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    video_dir = os.path.join(
        os.path.dirname(instance.video_file.path), str(instance.id)
    )
    if os.path.isdir(video_dir):
        shutil.rmtree(video_dir)