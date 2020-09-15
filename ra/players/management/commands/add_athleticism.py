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
            'id', 'priority', 'interception', 'sack', 'touchdown', 'avg_yards_of_seperation',
            'avg_closing_speed', 'top_speed', 'avg_transition_time',
            'time_to_top_speed', 'athleticism', 'play_making', 'film_grade', ).order_by('priority')
        for player in players:
            avg_yrd_separation =  player.avg_yards_of_seperation
            avgclospeed =player.avg_closing_speed
            topspeed = player.top_speed
            avgtranstime = player.avg_transition_time
            timetotopspeed = player.time_to_top_speed
            # avg_yrd_separation = athleticism_analyze['avg_yards_of_seperation']
            # avgtranstime = athleticism_analyze['avg_transition_time']
            # topspeed = athleticism_analyze['top_speed']
            # avgclospeed = athleticism_analyze['avg_closing_speed']
            # timetotopspeed = athleticism_analyze['time_to_top_speed']
            # athleticism_dict = {}
            # athleticism_dict['avg_yards_of_seperation'] = avg_yrd_separation
            # athleticism_dict['avg_closing_speed'] = avg_closing_speed
            # athleticism_dict['top_speed'] = topspeed
            # athleticism_dict['avg_transition_time'] = avg_transition_time
            # athleticism_dict['time_to_top_speed'] = timetotopspeed
            # athleticism_sco = get_athleticism(player, athleticism_dict)

            # Avg Yard of Sepeeration
            if avg_yrd_separation != None:
                if 0 <= avg_yrd_separation <= 0.99:
                    avg_yrd_separation_val = 100
                elif 1 < avg_yrd_separation <= 2.99:
                    avg_yrd_separation_val = 90
                elif 3 <= avg_yrd_separation <= 4.99:
                    avg_yrd_separation_val = 80
                elif 5 <= avg_yrd_separation <= 6.99:
                    avg_yrd_separation_val = 70
                elif 7 <= avg_yrd_separation <= 9.99:
                    avg_yrd_separation_val = 60
                elif 10 <= avg_yrd_separation <= 100:
                    avg_yrd_separation_val = 50
                else:
                    avg_yrd_separation_val = 0
            else:
                avg_yrd_separation_val = 0

            # Avg Transition Time
            if avgtranstime != None:
                if 0 <= avgtranstime < 0.1:
                    avgtranstime_val = 100
                elif 0.1 <= avgtranstime <= 0.29:
                    avgtranstime_val = 90
                elif 0.3 <= avgtranstime <= 0.49:
                    avgtranstime_val = 80
                elif 0.5 <= avgtranstime <= 0.69:
                    avgtranstime_val = 70
                elif 0.7 <= avgtranstime <= 0.89:
                    avgtranstime_val = 60
                elif avgtranstime > 0.89:
                    avgtranstime_val = 50
                else:
                    avgtranstime_val = 0
            else:
                avgtranstime_val = 0

            # Top Speed
            if topspeed != None:
                if topspeed >= 20:
                    topspeed_val = 100
                elif 18 <= topspeed <= 19.99:
                    topspeed_val = 90
                elif 16 <= topspeed <= 17.99:
                    topspeed_val = 80
                elif 14 <= topspeed <= 15.99:
                    topspeed_val = 70
                elif 12 <= topspeed <= 13.99:
                    topspeed_val = 60
                elif 0 <= topspeed < 12:
                    topspeed_val = 50
                else:
                    topspeed_val = 0
            else:
                topspeed_val = 0

            # Avg Closing Speed
            if avgclospeed != None:
                if 0 <= avgclospeed < 0.1:
                    avgclospeed_val = 100
                elif 0.1 <= avgclospeed <= 0.39:
                    avgclospeed_val = 90
                elif 0.4 <= avgclospeed <= 0.59:
                    avgclospeed_val = 80
                elif 0.6 <= avgclospeed <= 0.79:
                    avgclospeed_val = 70
                elif 0.8 <= avgclospeed <= 0.99:
                    avgclospeed_val = 60
                elif avgclospeed > 0.99:
                    avgclospeed_val = 50
                else:
                    avgclospeed_val = 0
            else:
                avgclospeed_val = 0

            # Time To Top Speed
            if timetotopspeed != None:
                if 0 <= timetotopspeed < 0.1:
                    timetotopspeed_val = 100
                elif 0.1 <= timetotopspeed <= 0.29:
                    timetotopspeed_val = 90
                elif 0.3 <= timetotopspeed <= 0.49:
                    timetotopspeed_val = 80
                elif 0.5 <= timetotopspeed <= 0.69:
                    timetotopspeed_val = 70
                elif 0.7 <= timetotopspeed <= 0.89:
                    timetotopspeed_val = 60
                elif timetotopspeed >= 0.9:
                    timetotopspeed_val = 50
                else:
                    timetotopspeed_val = 0
            else:
                timetotopspeed_val = 0

            # Avg Yard of Sepeeration Percentage
            if avg_yrd_separation_val:
                if avg_yrd_separation_val == 100:
                    avg_yrd_separation_score = 30
                    avg_yrd_separation__perc = 5
                elif avg_yrd_separation_val == 90:
                    avg_yrd_separation_score = 27
                    avg_yrd_separation__perc = 4
                elif avg_yrd_separation_val == 80:
                    avg_yrd_separation_score = 24
                    avg_yrd_separation__perc = 3
                elif avg_yrd_separation_val == 70:
                    avg_yrd_separation_score = 21
                    avg_yrd_separation__perc = 2
                elif avg_yrd_separation_val == 60:
                    avg_yrd_separation_score = 18
                    avg_yrd_separation__perc = 1
                elif avg_yrd_separation_val == 50:
                    avg_yrd_separation_score = 15
                    avg_yrd_separation__perc = 0
                else:
                    avg_yrd_separation_score = 0
                    avg_yrd_separation__perc = 0
            else:
                avg_yrd_separation_score = 0
                avg_yrd_separation__perc = 0

            # Avg Transition Time Percentage
            if avgtranstime != None:
                if avgtranstime_val == 100:
                    avgtranstime_score = 15
                    avgtranstime_perc = 5
                elif avgtranstime_val == 90:
                    avgtranstime_score = 13.5
                    avgtranstime_perc = 4
                elif avgtranstime_val == 80:
                    avgtranstime_score = 12
                    avgtranstime_perc = 3
                elif avgtranstime_val == 70:
                    avgtranstime_score = 10.5
                    avgtranstime_perc = 2
                elif avgtranstime_val == 60:
                    avgtranstime_score = 9
                    avgtranstime_perc = 1
                elif avgtranstime_val == 50:
                    avgtranstime_score = 7.5
                    avgtranstime_perc = 0
                else:
                    avgtranstime_score = 0
                    avgtranstime_perc = 0
            else:
                avgtranstime_score = 0
                avgtranstime_perc = 0

            # Top Speed Percentage
            if topspeed != None:
                if topspeed_val == 100:
                    topspeed_score = 20
                    topspeed_perc = 5
                elif topspeed_val == 90:
                    topspeed_score = 18
                    topspeed_perc = 4
                elif topspeed_val == 80:
                    topspeed_score = 16
                    topspeed_perc = 3
                elif topspeed_val == 70:
                    topspeed_score = 14
                    topspeed_perc = 2
                elif topspeed_val == 60:
                    topspeed_score = 12
                    topspeed_perc = 1
                elif topspeed_val == 50:
                    topspeed_score = 10
                    topspeed_perc = 0
                else:
                    topspeed_score = 0
                    topspeed_perc = 0
            else:
                topspeed_score = 0
                topspeed_perc = 0

            # Avg Closing Speed Percentage
            if avgclospeed != None:
                if avgclospeed_val == 100:
                    avgclospeed_score = 20
                    avgclospeed_perc = 5
                elif avgclospeed_val == 90:
                    avgclospeed_score = 18
                    avgclospeed_perc = 4
                elif avgclospeed_val == 80:
                    avgclospeed_score = 16
                    avgclospeed_perc = 3
                elif avgclospeed_val == 70:
                    avgclospeed_score = 14
                    avgclospeed_perc = 2
                elif avgclospeed_val == 60:
                    avgclospeed_score = 12
                    avgclospeed_perc = 1
                elif avgclospeed_val == 50:
                    avgclospeed_score = 10
                    avgclospeed_perc = 0
                else:
                    avgclospeed_score = 0
                    avgclospeed_perc = 0
            else:
                avgclospeed_score = 0
                avgclospeed_perc = 0

            # Time To Top Speed Percentage
            if timetotopspeed != None:
                if timetotopspeed_val == 100:
                    timetotopspeed_score = 15
                    timetotopspeed_perc = 5
                elif timetotopspeed_val == 90:
                    timetotopspeed_score = 13.5
                    timetotopspeed_perc = 4
                elif timetotopspeed_val == 80:
                    timetotopspeed_score = 12
                    timetotopspeed_perc = 3
                elif timetotopspeed_val == 70:
                    timetotopspeed_score = 10.5
                    timetotopspeed_perc = 2
                elif timetotopspeed_val == 60:
                    timetotopspeed_score = 9
                    timetotopspeed_perc = 1
                elif timetotopspeed_val == 50:
                    timetotopspeed_score = 7.5
                    timetotopspeed_perc = 0
                else:
                    timetotopspeed_score = 0
                    timetotopspeed_perc = 0

            else:
                timetotopspeed_score = 0
                timetotopspeed_perc = 0

            athleticism_score = (avg_yrd_separation_score + avgtranstime_score +
                                topspeed_score + avgclospeed_score + timetotopspeed_score
                                )
            if athleticism_score >= 1:
                player.athleticism = athleticism_score
                player.save()
            else:
                player.athleticism = None
                player.save()

            print(player.full_name, ' athleticism updated successfully')
