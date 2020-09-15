import io
import json
import os.path
import re
import urllib.request as urllib2
from django.conf import settings
import xlrd
from django.core.management.base import BaseCommand
import ssl
from players.models import Player
import ast


class Command(BaseCommand):
    """
        Use Case: python manage.py update
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/play_making.xlsx
    """
    help = 'Used to Importing Players Play Making data from Excel File.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        data = []
        xlsx_file = xlrd.open_workbook(options['file'])
        worksheet = xlsx_file.sheet_by_index(0)
        offset = 0
        for i, row in enumerate(range(worksheet.nrows)):
            if i <= offset:
                continue
            row_data = []
            for j, col in enumerate(range(1, worksheet.ncols+1)):
                row_data.append(worksheet.cell_value(i, j))
            data.append(row_data)
        print("player has beed adding...")
        print(".........")
        for player in data:
            try:
                priority = int(player[0])
                interception_raw_score_val = player[2]
                sacks_raw_score_val = player[3]
                touchdowns_raw_score_val = player[4]
                if interception_raw_score_val != (None or ''):
                    interception_raw_score = interception_raw_score_val
                else:
                    interception_raw_score = None
                if sacks_raw_score_val != (None or ''):
                    sacks_raw_score = sacks_raw_score_val
                else:
                    sacks_raw_score = None
                if touchdowns_raw_score_val != (None or ''):
                    touchdowns_raw_score = touchdowns_raw_score_val
                else:
                    touchdowns_raw_score = None

                if interception_raw_score:
                    if 0 < interception_raw_score == 1.99:
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
                if sacks_raw_score:
                    if 0 < sacks_raw_score <= 2.99:
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
                if touchdowns_raw_score:
                    if 0 < touchdowns_raw_score <= 2.99:
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

                if interception_val:
                    if interception_val == 100:
                        interception_score = 55
                        interception_score_perc = 5
                    elif interception_val == 90:
                        interception_score = 49.5
                        interception_score_perc = 4
                    elif interception_val == 80:
                        interception_score = 44
                        interception_score_perc = 3
                    elif interception_val == 70:
                        interception_score = 38.5
                        interception_score_perc = 2
                    elif interception_val == 60:
                        interception_score = 33
                        interception_score_perc = 1
                    else:
                        interception_score = 0
                        interception_score_perc = 0
                else:
                    interception_score = 0
                    interception_score_perc = 0
                if sack_val:
                    if sack_val == 100:
                        sack_score = 15
                        sack_score_perc = 5
                    elif sack_val == 90:
                        sack_score = 13.5
                        sack_score_perc = 4
                    elif sack_val == 80:
                        sack_score = 12
                        sack_score_perc = 3
                    elif sack_val == 70:
                        sack_score = 10.5
                        sack_score_perc = 2
                    elif sack_val == 60:
                        sack_score = 9
                        sack_score_perc = 1
                    else:
                        sack_score = 0
                        sack_score_perc = 0
                else:
                    sack_score = 0
                    sack_score_perc = 0
                if touchdown_val:
                    if touchdown_val == 100:
                        touchdown_score = 30
                        touchdown_score_perc = 5
                    elif touchdown_val == 90:
                        touchdown_score = 27
                        touchdown_score_perc = 4
                    elif touchdown_val == 80:
                        touchdown_score = 24
                        touchdown_score_perc = 3
                    elif touchdown_val == 70:
                        touchdown_score = 21
                        touchdown_score_perc = 2
                    elif touchdown_val == 60:
                        touchdown_score = 18
                        touchdown_score_perc = 1
                    else:
                        touchdown_score = 0
                        touchdown_score_perc = 0
                else:
                    touchdown_score = 0
                    touchdown_score_perc = 0

                playmaking_score = (interception_score +
                                    sack_score+touchdown_score)
                if interception_val is not 0:
                    interception_play_making_raw = (
                        interception_score * interception_score_perc) / interception_val
                if sack_val is not 0:
                    sack_play_making_raw = (
                        sack_score * sack_score_perc) / sack_val
                if touchdown_val is not 0:
                    touchdown_play_making_raw = (
                        touchdown_score * touchdown_score_perc) / touchdown_val
                total_play_making = (
                    interception_play_making_raw + sack_play_making_raw + touchdown_play_making_raw)
                player = Player.objects.filter(priority=priority)
                if player:
                    if playmaking_score > 0:
                        player[0].play_making = playmaking_score
                    else:
                        player[0].play_making = None
                    if total_play_making >= 1:
                        player[0].play_making_raw_score = total_play_making
                    else:
                        player[0].play_making_raw_score = None

                    player[0].save()
                    print('{} {}'.format(player[0].full_name,player[0].play_making))

            except Exception as e:
                print(e)
