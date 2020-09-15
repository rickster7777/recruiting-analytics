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
                team_name = player[10].strip().title()
                team_logo = player[11]
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
                height_val = str(player[6])
                if height_val != None and height_val != '' and\
                        height_val != '.' and height_val != '0':
                    # player_height = float(height_val)
                    if len(height_val) == 1:
                        feet = int(height_val)
                        inches = 0
                        player_height = (feet*12 + inches)
                    else:
                        if len(height_val) >= 3:
                            list_obj = height_val.split('.')
                            feet = int(list_obj[0])
                        if len(list_obj) >= 2:
                            inches = int(list_obj[1])
                        else:
                            inches = 0
                    height = (feet*12 + inches)
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

                player_obj = Player.objects.get(
                    role__name__iexact='nfl',
                    full_name=full_name
                )
                # player_obj.height = height

                if team_name:
                    try:
                        nfl_team = Team.objects.get(name__iexact=team_name)
                        if nfl_team:
                            if team_logo:
                                try:
                                    img_url = team_logo
                                    ssl._create_default_https_context = ssl._create_unverified_context
                                    result = urllib2.urlretrieve(img_url)
                                    nfl_team.logo.save(
                                        os.path.basename(img_url),
                                        File(open(result[0], 'rb'))
                                    )
                                    nfl_team.save()
                                except Exception as e:
                                    print("{} NFL Team logo not found in given URL {}".format(
                                        nfl_team.name, e))
                    except Team.DoesNotExist:
                        nfl_team = Team.objects.create(name=team_name)
                        if team_logo:
                            try:
                                img_url = team_logo
                                ssl._create_default_https_context = ssl._create_unverified_context
                                result = urllib2.urlretrieve(img_url)
                                nfl_team.logo.save(
                                    os.path.basename(img_url),
                                    File(open(result[0], 'rb'))
                                )
                                nfl_team.save()
                            except Exception as e:
                                print("{} NFL Team logo not found in given URL {}".format(
                                    nfl_team.name, e))
                nfllogo = "https://cdn.freebiesupply.com/logos/large/2x/nfl-1-logo-png-transparent.png"
                try:
                    img_url = nfllogo
                    ssl._create_default_https_context = ssl._create_unverified_context
                    result = urllib2.urlretrieve(img_url)
                    player_obj.nfl_logo.save(
                        os.path.basename(img_url),
                        File(open(result[0], 'rb'))
                    )
                    player_obj.save()
                except Exception as e:
                    print("{} Player Avatar not found in given URL {}".format(
                        player.name, e))
                if school:
                    player_obj.school = school
                player_obj.team = nfl_team
                player_obj.save()
                db = ['CB', 'S', 'SS', 'FS', 'DB']
                player_obj.position.clear()
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
                    player_obj.position.add(position.id)
                    player_obj.save()
                player_obj.save()
                # Play making scores logic
                interception_raw_score_val = player[12]
                sacks_raw_score_val = player[13]
                touchdowns_raw_score_val = player[14]
                if interception_raw_score_val != (None or ''):
                    player_obj.interception = float(interception_raw_score_val)
                    interception_raw_score = interception_raw_score_val
                else:
                    interception_raw_score = None
                if sacks_raw_score_val != (None or ''):
                    player_obj.sack = float(sacks_raw_score_val)
                    sacks_raw_score = sacks_raw_score_val
                else:
                    sacks_raw_score = None
                if touchdowns_raw_score_val != (None or ''):
                    player_obj.touchdown = float(touchdowns_raw_score_val)
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
                    elif 6 <= interception_val <= 7.9:
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
                    if 1 <= touchdowns_raw_score <= 2.99:
                        touchdown_val = 60
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

                playmaking_score = (interception_score +
                                    sack_score+touchdown_score)
                interception_play_making_raw = 0
                sack_play_making_raw = 0
                interception_play_making_raw = 0
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
                
                if player_obj:
                    if playmaking_score > 0:
                        player_obj.play_making = playmaking_score
                    else:
                        player_obj.play_making = None
                    if total_play_making > 0:
                        player_obj.play_making_raw_score = total_play_making
                player_obj.save()

            except Exception as e:
                print(e)
        print('All NFL Players updated successfully')
