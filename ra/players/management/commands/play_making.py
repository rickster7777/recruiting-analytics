import io
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from players.models import Player
from players.performance_data import get_athleticism


class Command(BaseCommand):
    """
        Use Case: python manage.py add_film_grades
    """
    help = 'Used to adding Playmaking score.'

    def handle(self, *args, **options):
        players = Player.objects.only(
            'id', 'interception', 'sack', 'touchdown', 'avg_yards_of_seperation',
            'avg_closing_speed', 'top_speed', 'avg_transition_time',
            'time_to_top_speed', 'athleticism', 'play_making', 'film_grade', )
        for player in players:

            interception_raw_score_val = player.interception
            sacks_raw_score_val = player.sack
            touchdowns_raw_score_val = player.touchdown
            if interception_raw_score_val != (None and ''):
                interception_raw_score = interception_raw_score_val
            else:
                interception_raw_score = None
            if sacks_raw_score_val != (None and ''):
                sacks_raw_score = sacks_raw_score_val
            else:
                sacks_raw_score = None
            if touchdowns_raw_score_val != (None and ''):
                touchdowns_raw_score = touchdowns_raw_score_val
            else:
                touchdowns_raw_score = None

            if interception_raw_score != None:
                if 0 <= interception_raw_score <= 0.99:
                    interception_val = 50
                elif 1 <= interception_raw_score <= 1.99:
                    interception_val = 60
                elif 2 <= interception_raw_score <= 3.99:
                    interception_val = 70
                elif 4 <= interception_raw_score <= 5.99:
                    interception_val = 80
                elif 6 <= interception_raw_score <= 7.99:
                    interception_val = 90
                elif interception_raw_score >= 8:
                    interception_val = 100
                else:
                    interception_val = 0
            else:
                interception_val = 0
            if sacks_raw_score != None:
                if 0 <= sacks_raw_score <= 0.99:
                    sack_val = 50
                elif 1 <= sacks_raw_score <= 2.99:
                    sack_val = 60
                elif 3 <= sacks_raw_score <= 4.99:
                    sack_val = 70
                elif 5 <= sacks_raw_score <= 6.99:
                    sack_val = 80
                elif 7 <= sacks_raw_score <= 8.99:
                    sack_val = 90
                elif sacks_raw_score >= 9:
                    sack_val = 100
                else:
                    sack_val = 0
            else:
                sack_val = 0
            if touchdowns_raw_score != None:
                if 0 <= touchdowns_raw_score <= 0.99:
                    touchdown_val = 50
                elif 1 <= touchdowns_raw_score <= 2.99:
                    touchdown_val = 60
                elif 3 <= touchdowns_raw_score <= 4.99:
                    touchdown_val = 70
                elif 5 <= touchdowns_raw_score <= 6.99:
                    touchdown_val = 80
                elif 7 <= touchdowns_raw_score <= 8.99:
                    touchdown_val = 90
                elif touchdowns_raw_score >= 9:
                    touchdown_val = 100
                else:
                    touchdown_val = 0
            else:
                touchdown_val = 0

            if interception_val != None:
                if interception_val == 100:
                    interception_score = 55
                    interception_score_perc = 6
                elif interception_val == 90:
                    interception_score = 49.5
                    interception_score_perc = 5
                elif interception_val == 80:
                    interception_score = 44
                    interception_score_perc = 4
                elif interception_val == 70:
                    interception_score = 38.5
                    interception_score_perc = 3
                elif interception_val == 60:
                    interception_score = 33
                    interception_score_perc = 2
                elif interception_val == 50:
                    interception_score = 27.5
                    interception_score_perc = 1
                else:
                    interception_score = 0
                    interception_score_perc = 0
            else:
                interception_score = 0
                interception_score_perc = 0
            if sack_val != None:
                if sack_val == 100:
                    sack_score = 15
                    sack_score_perc = 6
                elif sack_val == 90:
                    sack_score = 13.5
                    sack_score_perc = 5
                elif sack_val == 80:
                    sack_score = 12
                    sack_score_perc = 4
                elif sack_val == 70:
                    sack_score = 10.5
                    sack_score_perc = 3
                elif sack_val == 60:
                    sack_score = 9
                    sack_score_perc = 2
                elif sack_val == 50:
                    sack_score = 7.5
                    sack_score_perc = 1
                else:
                    sack_score = 0
                    sack_score_perc = 0
            else:
                sack_score = 0
                sack_score_perc = 0
            if touchdown_val != None:
                if touchdown_val == 100:
                    touchdown_score = 30
                    touchdown_score_perc = 6
                elif touchdown_val == 90:
                    touchdown_score = 27
                    touchdown_score_perc = 5
                elif touchdown_val == 80:
                    touchdown_score = 24
                    touchdown_score_perc = 4
                elif touchdown_val == 70:
                    touchdown_score = 21
                    touchdown_score_perc = 3
                elif touchdown_val == 60:
                    touchdown_score = 18
                    touchdown_score_perc = 2
                elif touchdown_val == 50:
                    touchdown_score = 15
                    touchdown_score_perc = 1
                else:
                    touchdown_score = 0
                    touchdown_score_perc = 0
            else:
                touchdown_score = 0
                touchdown_score_perc = 0

            playmaking_score = (interception_score +
                                sack_score+touchdown_score)
            if interception_val != 0:
                interception_play_making_raw = (
                    interception_score * interception_score_perc) / interception_val
            else:
                interception_play_making_raw = 0
            if sack_val != 0:
                sack_play_making_raw = (
                    sack_score * sack_score_perc) / sack_val
            else:
                sack_play_making_raw = 0
            if touchdown_val != 0:
                touchdown_play_making_raw = (
                    touchdown_score * touchdown_score_perc) / touchdown_val
            else:
                touchdown_play_making_raw = 0
            total_play_making = (
                interception_play_making_raw + sack_play_making_raw + touchdown_play_making_raw)
            if playmaking_score >= 1:
                player.play_making = playmaking_score
            else:
                player.play_making = None
            if total_play_making > 0:
                player.play_making_raw_score = total_play_making
            else:
                player.play_making_raw_score = None
            player.save()

            avg_yrd_separation =  player.avg_yards_of_seperation
            avg_closing_speed =player.avg_closing_speed
            topspeed = player.top_speed
            avg_transition_time = player.avg_transition_time
            timetotopspeed = player.time_to_top_speed
            athleticism_dict = {}
            athleticism_dict['avg_yards_of_seperation'] = avg_yrd_separation
            athleticism_dict['avg_closing_speed'] = avg_closing_speed
            athleticism_dict['top_speed'] = topspeed 
            athleticism_dict['avg_transition_time'] = avg_transition_time
            athleticism_dict['time_to_top_speed'] = timetotopspeed
            athleticism_sco = get_athleticism(player, athleticism_dict)
        print("Athleticism score for all players updated")
