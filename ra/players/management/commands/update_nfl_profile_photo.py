import ast
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

from address.models import School
from players.models import Player, PlayerType, PositionGroup, Positions, Team


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

        for player in data:
            try:
                profile_photo = player[4]
                first_name = player[0].strip()
                last_name = player[1].strip()
                full_name = first_name + ' ' + last_name
                player_obj = Player.objects.get(
                    role__name__iexact='nfl',
                    full_name=full_name
                )

                try:
                    if profile_photo:
                        img_url = profile_photo.strip()
                        ssl._create_default_https_context = ssl._create_unverified_context
                        result = urllib2.urlretrieve(img_url)
                        player_obj.profile_photo.save(
                            os.path.basename(img_url),
                            File(open(result[0], 'rb'))
                        )
                        player_obj.save()
                except Exception as e:
                    print("{} NFL Team logo not found in given URL {}".format(
                        player_obj.first_name, e))
            except Exception as e:
                print(e)
                print('All NFL Players updated successfully')
