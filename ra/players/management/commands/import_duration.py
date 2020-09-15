import io
import subprocess
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from players.models import Player


class Command(BaseCommand):
    """
        Use Case: python manage.py import_duration
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
                if 'Highlights Video Not Uploaded' not in video:
                    result = subprocess.run(
                        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1', video
                        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    )
                    try:
                        total_seconds = float(result.stdout)
                        video_length = time.strftime("%M:%S", time.gmtime(total_seconds))
                        player.video_highlight_duration = video_length
                        player.save()
                    except ValueError:
                        print(player.full_name, 'video access denied')
                    # video_length = time.strftime("%M:%S", time.gmtime(total_seconds))
                    # player.video_highlight_duration = video_length
                    # player.save()
            except Exception as e:
                print(e, player.full_name)
