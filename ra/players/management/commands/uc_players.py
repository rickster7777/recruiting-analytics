import io
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from players.models import Player, PlayerType


class Command(BaseCommand):
    help = 'Used to Tag UC Types in Players.'

    def handle(self, *args, **options):
        nfl_players = Player.objects.filter(
            role__name__iexact='nfl', film_grade__isnull=False).distinct()

        for nfl in nfl_players:
            nfl_filmgrade = nfl.film_grade
            nfl_height = nfl.height
            nfl_weight = nfl.weight
            nfl_positions = nfl.position.all()
            filters = {}
            filters['film_grade__isnull'] = False
            filters['height__isnull'] = False
            filters['weight__isnull'] = False

            all_uc_players = Player.objects.only('role', 'film_grade',
                                                           'height', 'weight',
                                                           'classification',
                                                           'position').filter(
                Q(
                    Q(**filters) &
                    Q(role__name__in=['prospect', 'undercruited']) &
                    Q(film_grade__lte=nfl_filmgrade + 3.0) &
                    Q(film_grade__gte=nfl_filmgrade - 3.0)
                ) &
                Q(
                    (
                        Q(height__lte=nfl_height + 1) &
                        Q(height__gte=nfl_height - 1)
                    ) &
                    (
                        Q(weight__lte=nfl_weight + 15.0) &
                        Q(weight__gte=nfl_weight - 15.0)
                    )
                )
            ).distinct()

            for uc_player in all_uc_players:
                role = PlayerType.objects.get(name='undercruited')
                uc_player.role = role
                uc_player.save()
                print("{} particular NFl player tagged successfully for UnderCruited Player".format(
                    nfl.first_name))
        print("......")
        print(".............")
        print("........................")
        print("All player tagged successfully for UnderCruited")
