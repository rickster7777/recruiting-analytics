import io
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from players.models import Player


class Command(BaseCommand):
    """
        Use Case: python manage.py add_film_grades
    """
    help = 'Used to Importing FilmGrade Data from Athleticism score and \
        Playmaking score.'

    def handle(self, *args, **options):
        athleticism_players = Player.objects.filter(
            Q(athleticism__isnull=False) |
            Q(play_making__isnull=False)
        )
        if athleticism_players:
            for player in athleticism_players:
                if (player.athleticism is not None) and (player.play_making is not None):
                    film_grade = (player.athleticism + player.play_making) / 2
                    player.film_grade = film_grade
                elif (player.athleticism is not None) and (player.play_making is None):
                    film_grade = (player.athleticism + 0) / 2
                    player.film_grade = film_grade
                elif (player.athleticism is None) and (player.play_making is not None):
                    film_grade = (0 + player.play_making) / 2
                    player.film_grade = film_grade
                else:
                    player.film_grade = None
                player.save()
                print("'{}' player has been updated with film grade \
                    successfully".format(player.full_name))
