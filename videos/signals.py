from django.db.models.signals import post_save
from django.dispatch import receiver
import django_rq
from .models import Video
from .tasks import convert_video_to_hls


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):

    if created and instance.video_file:

        django_rq.enqueue(convert_video_to_hls, instance.id)
