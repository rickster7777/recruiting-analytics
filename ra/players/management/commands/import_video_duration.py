import io
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Player
from moviepy.editor import VideoFileClip
import time


class Command(BaseCommand):
    """
        Use Case: python manage.py import_video_duration
    """
    help = 'Used to Importing Video duration Data from Highlighted Video.'

    def handle(self, *args, **options):
        players = Player.objects.filter(
            video_highlight__isnull=False,
            video_highlight_duration__isnull=True
        )
        for player in players:
            try:
                video = player.video_highlight
                video_info = VideoFileClip(video)
                total_seconds = video_info.duration
                video_length = time.strftime("%M:%S", time.gmtime(total_seconds))
                player.video_highlight_duration = video_length
                player.save()

            except Exception as e:
                print(e, player.full_name)
