"""
Management utility to create Players Types.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from players.models import PlayerType

User = get_user_model()


class Command(BaseCommand):
    help = 'Used to create Players Types.'

    def handle(self, *args, **options):

        player_types = ['prospect', 'futurestar',
                        'undercruited', 'nfl']

        for player_type in player_types:
            player_role, created = PlayerType.objects.get_or_create(
                name=player_type
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        "New Player Role '{}' added successfully.".format(
                            player_type)
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "Player Role '{}' already added.".format(
                            player_type)
                    )
                )
