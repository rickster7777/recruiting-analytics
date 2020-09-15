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

        for player in data:
            try:
                first_name = player[0].strip()
                last_name = player[1].strip()
                full_name = first_name + ' ' + last_name
                school_name = player[2].strip()
                pos = player[3].strip()
                logo = player[4]
                jersey_no = player[5]
                if jersey_no:
                    jersey = int(jersey_no)
                else:
                    jersey = None
                height_val = player[6]
                if height_val:
                    height = float(height_val)
                else:
                    height = None
                weight_val = player[7]
                if weight_val:
                    weight = float(weight_val)
                else:
                    weight = None
                twitterhandle = player[8]
                if twitterhandle:
                    handle = twitterhandle.strip()
                else:
                    handle = None
                collegelogo = player[9]

                school, created = School.objects.get_or_create(
                    name=school_name
                )
                school_logo = player[9]
                if school_logo:
                    schoolLogo = school_logo.strip()
                    try:
                        if schoolLogo:
                            img_url = schoolLogo
                            ssl._create_default_https_context = ssl._create_unverified_context
                            result = urllib2.urlretrieve(img_url)
                            # image_name = img_url.split('/')[-1]
                            school.logo.save(
                                os.path.basename(img_url),
                                File(open(result[0], 'rb'))
                            )

                    except Exception as e:
                        print("{} School Logo not found in given URL {}".format(
                            full_name, e))

                player = Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    weight=weight,
                    jersey_number=jersey,
                    twitter_handle=handle
                )
                player_role = PlayerType.objects.get(
                    name='nfl'
                )

                player.role = player_role
                player.school = school
                player.save()
                db = ['CB', 'S', 'SS', 'FS', 'DB']
                if pos in db:
                    pos_group = 'DB'
                    position_group, created = PositionGroup.objects.get_or_create(
                        name=pos_group
                    )
                    position, created = Positions.objects.get_or_create(
                        name=pos,
                    )
                    position.group = position_group
                    position.save()
                    player.position.add(position.id)
                    player.save()
                logo = "https://cdn.freebiesupply.com/logos/large/2x/nfl-1-logo-png-transparent.png"
                try:
                    img_url = logo
                    ssl._create_default_https_context = ssl._create_unverified_context
                    result = urllib2.urlretrieve(img_url)
                    player.nfl_logo.save(
                        os.path.basename(img_url),
                        File(open(result[0], 'rb'))
                    )
                    player.save()
                except Exception as e:
                    print("{} Player Avatar not found in given URL {}".format(
                        player.name, e))

                try:
                    if logo:
                        img_url = logo
                        ssl._create_default_https_context = ssl._create_unverified_context
                        result = urllib2.urlretrieve(img_url)
                        player.profile_photo.save(
                            os.path.basename(img_url),
                            File(open(result[0], 'rb'))
                        )
                        player.save()
                except Exception as e:
                    print("{} Player Avatar not found in given URL {}".format(
                        full_name, e))
                player.save()

            except Exception as e:
                print(e)
