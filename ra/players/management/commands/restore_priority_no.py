import argparse
import ast
import csv
import io
import json
import os.path
import re
import ssl
import urllib.request as urllib2

import xlrd
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Max

from players.models import Player


class Command(BaseCommand):
    """
        Use Case: python manage.py new_player_import_30_april
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/player_unique28April.xlsx
    """
    help = 'Used for Importing New Players  Data from Excel File.'

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
        print(".........")
        priorityobj = Player.objects.aggregate(Max('priority'))
        priority_val = priorityobj['priority__max']
        all_ids = []
        for player in data:
            not_found_list = []
            try:
                player_id = player[0]
                player_priority = int(player[9])
                try:
                    player_obj = Player.objects.get(id=player_id)
                    player_obj.priority = player_priority
                    player_obj.save()
                    all_ids.append(player_id)
                    print(player_id, ' - player found')
                except Player.DoesNotExist:
                    # not_found_list.append(player_id)
                    # with open('/home/kapil/Desktop/ra_repo/ra/ra/players/management/old-may-new_not_found_players_list.csv', 'a') as ff:
                    #     writer = csv.writer(ff)
                    #     writer.writerow(not_found_list)
                    #     not_found_list = []
                    print(player_id, ' - PLAYER NOT FOUND')
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        print('ssucc')
        last_priority_no = Player.objects.get(id=all_ids[-1]).priority
        all_players = Player.objects.all().exclude(
            id__in=all_ids).order_by('priority')
        for player in all_players:
            player.priority = last_priority_no + 1
            player.save()
            last_priority_no = last_priority_no + 1
            print(player.id, ' :- player has been updated successfully')

        print("----------****----------")
        print("All players priority no's updated successfully!")
        print("----------****----------")
