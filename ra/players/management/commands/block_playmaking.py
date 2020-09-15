from django.core.management.base import BaseCommand
from players.models import OldPlayMakingValues, Player


class Command(BaseCommand):
    """
        Use Case: python manage.py block_playmaking
    """
    help = 'Used for storing playmaking and athleticism score values'

    def handle(self, *args, **options):
        players = Player.objects.all().order_by('priority')
        for player in players:
            try:
                old_obj = OldPlayMakingValues.objects.filter(player=player)
                if old_obj:
                    old_obj = old_obj[0]
                    old_obj.old_avg_transition_time = player.avg_transition_time
                    old_obj.old_avg_closing_speed = player.avg_closing_speed
                    old_obj.old_avg_yards_of_seperation = player.avg_yards_of_seperation
                    old_obj.old_top_speed = player.top_speed
                    old_obj.old_time_to_top_speed = player.time_to_top_speed
                    old_obj.save()
                else:
                    OldPlayMakingValues.objects.create(
                        player=player,
                        old_interception_maxpreps=player.interception,
                        old_sack_maxpreps=player.sack,
                        old_touchdown_maxpreps=player.touchdown,
                        old_avg_transition_time=player.avg_transition_time,
                        old_avg_closing_speed=player.avg_closing_speed,
                        old_avg_yards_of_seperation=player.avg_yards_of_seperation,
                        old_top_speed=player.top_speed,
                        old_time_to_top_speed=player.time_to_top_speed,
                    )

            except Exception as e:
                print(e)
        print("----------****----------")
        print("All play makaing & Athleticism values has been updated successfully")
        print("----------****----------")
