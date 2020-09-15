import ast
import io
import json
import os.path
import re
import ssl
import urllib.request as urllib2
import csv
import xlrd
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from address.models import School
from players.models import Player, PlayerType, PositionGroup, Positions


class Command(BaseCommand):
    """
        Use Case: python manage.py player_import
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/import_players.xlsx
    """
    help = 'Used to Importing Players Data from Excel File.'

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
        list_obj = []
        list_l = []
        for player_data in data:
            raw_top_speed = player_data[3]
            raw_top_speed_time = player_data[4]
            raw_transition_time = player_data[9]
            if raw_transition_time != None and raw_transition_time != '':
                player_transiton_time = raw_transition_time
            else:
                player_transiton_time = None
            raw_video = player_data[10]
            if raw_video != None and raw_video != '':
                player_video = raw_video
            else:
                player_video = None
            if raw_top_speed != None and raw_top_speed != '':
                player_top_speed = raw_top_speed
            else:
                player_top_speed = None
            if raw_top_speed_time != None and raw_top_speed_time != '':
                player_top_speed_time = raw_top_speed_time
            else:
                player_top_speed_time = None

            prio = player_data[0]
            p_name = player_data[1]
            p_id = player_data[2]
            ply = Player.objects.filter(
                full_name__iexact=p_name)
            if ply:
                player_obj = ply[0]
                if player_top_speed != None and player_top_speed != '':
                    if player_top_speed == 0:
                        player_obj.top_speed = player_top_speed
                    else:
                        top_speed_val = float("%.2f" % round(player_top_speed, 2))
                        player_obj.top_speed = top_speed_val
                if player_top_speed_time != None and player_top_speed_time != '':
                    if player_top_speed_time == 0:
                        player_obj.time_to_top_speed = player_top_speed_time
                    else:
                        timetotopspeed = float(
                            "%.2f" % round(player_top_speed_time, 2))
                        player_obj.time_to_top_speed = timetotopspeed
                if player_transiton_time != None and player_transiton_time != '':
                    if player_transiton_time == 0:
                        player_obj.avg_transition_time = player_transiton_time
                    else:
                        avg_transition_time_val = float(
                            "%.2f" % round(player_transiton_time, 2))
                        player_obj.avg_transition_time = avg_transition_time_val
                if player_video:
                    player_obj.video_highlight = \
                        "https://ra-processedv-videos.s3.us-east-2.amazonaws.com/"\
                            + player_video
                player_obj.save()
            else:
                print(p_name, ' not found')
