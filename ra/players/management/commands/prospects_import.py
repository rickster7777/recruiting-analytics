import io
import json
import os.path
import re
import urllib.request as urllib2
from django.conf import settings
import xlrd
from django.core.files import File
from django.core.management.base import BaseCommand
import ssl
from address.models import City, School, State
from players.models import (Classification, FbsHardCommit, FbsOffers, Player,
                            PlayerType, PositionGroup, Positions, SchoolsVisit)
import ast


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
        # PositionGroup.objects.all().delete()
        # Player.objects.all().delete()
        # Positions.objects.all().delete()
        # Classification.objects.all().delete()
        # School.objects.all().delete()
        print("player has beed adding...")
        print(".........")

        for player in data:
            if player[0] == 'Dyson Mccutcheon':
                print(player)
            try:
                full_name = player[0].strip()
                full_name = player[0].strip()
                first_name = player[0].split()[0].strip()
                first_name = player[0].split()[0].strip()
                if len(player[0].split()) >= 3:
                    last_name = player[0].split()[1].strip(
                    ) + player[0].split()[2].strip()
                else:
                    last_name = player[0].split()[1].strip()
                state_name = player[1].upper()
                city_name = player[2]
                high_school = player[3].replace('  ', ' ').strip()
                positions = player[4].split()
                rating = player[5]
                if rating:
                    star = int(rating)
                else:
                    star = None
                # if rating:
                #     if 0.0 <= rating <= 0.1999:
                #         star_rating = 1
                #     elif 0.2 <= rating <= 0.3999:
                #         star_rating = 2
                #     elif 0.4 <= rating <= 0.5999:
                #         star_rating = 3
                #     elif 0.6 <= rating <= 0.7999:
                #         star_rating = 4
                #     elif 0.8 <= rating >= 0.8:
                #         star_rating = 5
                #     else:
                #         star_rating = None
                # else:
                #     star_rating = None

                # fbs_offers = player[6]
                height = player[7]
                weight = player[8]
                forty = player[9]
                if forty:
                    forty = forty
                else:
                    forty = None
                short_shuttle = player[10]
                if short_shuttle:
                    short_shuttle = short_shuttle
                else:
                    short_shuttle = None
                vertical = player[11]
                if vertical:
                    vertical = vertical
                else:
                    vertical = None
                yr = player[12]
                jersey_no = player[13]
                twitter_handle = player[14]
                if twitter_handle is not '':
                    twitter_handle = player[14].strip()
                else:
                    twitter_handle = None
                avatar = player[15]
                priority_val = player[17]
                if priority_val:
                    priority = int(priority_val)
                else:
                    priority = None
                # if ranking:
                #     rank = int(ranking)
                # else:
                #     rank = None
                fbs_offers = player[6]
                if fbs_offers:
                    res = ast.literal_eval(fbs_offers)
                    total_offers = len(res.items())
                    if total_offers >= 1:
                        fbsoffers = FbsOffers.objects.create(
                            total=str(total_offers)
                        )

                        # res = ast.literal_eval(fbs_offers)
                        # total_offers = len(res.items())
                        for items in res.items():
                            list_obj = list(items[1])
                            list_obj.insert(0, items[0])
                            # print(list_obj)
                            school_name = list_obj[0]
                            if list_obj[1] is not '':
                                commited_date = list_obj[1].strip()
                            else:
                                commited_date = None
                            school_logo = list_obj[2]

                            school, created = School.objects.get_or_create(
                                name=school_name.strip(),
                            )
                            fbsoffers.schools.add(school)
                            fbsoffers.save()
                            if school_logo:
                                img_url = school_logo
                                ssl._create_default_https_context = ssl._create_unverified_context
                                result = urllib2.urlretrieve(img_url)
                                school.logo.save(
                                    os.path.basename(img_url),
                                    File(open(result[0], 'rb'))
                                )
                                school.save()
                            if list_obj[1] is not '':
                                fbs_hard_commit, created = FbsHardCommit.objects.get_or_create(
                                    school=school,
                                    commited_on=list_obj[2].strip()
                                )
                                fbsoffers.hard_commit = fbs_hard_commit
                                fbsoffers.save()

                # if len(positions) >= 0:
                #     for pos in positions:
                #         positions, created = Positions.objects.get_or_create(
                #             name=pos)
                #         if created:
                #             print("position successfully added")
                #         else:
                #             print("already exists")
                # else:
                #     positions = ''

                player_obj = Player.objects.create(
                    full_name=full_name.title(),
                    first_name=first_name.title(),
                    last_name=last_name.title(),
                    twitter_handle=twitter_handle,
                    fourty_yard_dash=forty,
                    short_shuttle=short_shuttle,
                    vertical=vertical,
                    priority=priority,
                )
                if state_name:
                    state, created = State.objects.get_or_create(
                        abbreviation=state_name.strip()
                    )
                    player_obj.state = state
                    player_obj.save()

                if city_name:
                    city, created = City.objects.get_or_create(
                        name=city_name.strip(),
                        state=state
                    )
                    player_obj.city = city
                    player_obj.save()

                player_role = PlayerType.objects.get(
                    name='prospect'
                )
                player_obj.role = player_role
                player_obj.save()
                if high_school:
                    highschool, created = School.objects.get_or_create(
                        name=high_school.strip(),
                    )
                    player_obj.school = highschool
                    player_obj.save()
                if fbs_offers:
                    player_obj.fbs_offers = fbsoffers
                try:
                    if avatar:
                        img_url = avatar
                        ssl._create_default_https_context = ssl._create_unverified_context
                        result = urllib2.urlretrieve(img_url)
                        # image_name = img_url.split('/')[-1]
                        player_obj.profile_photo.save(
                            os.path.basename(img_url),
                            File(open(result[0], 'rb'))
                        )
                        player_obj.save()
                except Exception as e:
                    print("{} Player Avatar not found in given URL {}".format(
                        full_name, e))

                # if created:
                if height is not '':
                    player_obj.height = float(height)
                    player_obj.save()
                if yr is not '':
                    yr = int(yr)
                    yr = re.sub(r"[^0-9]", "", str(yr))
                    year, created = Classification.objects.get_or_create(
                        year=str(yr)
                    )
                    player_obj.classification = year
                    player_obj.save()
                if jersey_no is not '':
                    player_obj.jersey_number = int(jersey_no)
                    player_obj.save()
                if weight is not '':
                    player_obj.weight = float(weight)
                    player_obj.save()
                if len(positions) > 0:
                    for pos in positions:
                        db = ['CB', 'S', 'SS', 'FS', 'DB']
                        rb = ['APB', 'RB', 'FB']
                        rec = ['WR', 'TE', 'R', 'T']
                        ol = ['OL', 'OT', 'OG', 'OC']
                        dl = ['DL', 'WDE', 'SDE', 'DT']
                        lb = ['LB', 'ILB', 'OLB']
                        qb = ['Pro', 'PRO', 'Dual', 'DUAL', 'QB']
                        Special = ['ATH', 'K', 'P', 'LS', 'RET']

                        pos = re.sub(r"[^a-zA-Z]", "", pos.upper())

                        if pos in db:
                            pos_group = 'DB'
                        elif pos in rb:
                            pos_group = 'RB'
                        elif pos in rec:
                            pos_group = 'R'
                        elif pos in ol:
                            pos_group = 'OL'
                        elif pos in dl:
                            pos_group = 'DL'
                        elif pos in lb:
                            pos_group = 'LB'
                        elif pos in qb:
                            pos_group = 'QB'
                        elif pos in Special:
                            pos_group = 'Special'
                        else:
                            pos_group = None

                        position_group, created = PositionGroup.objects.get_or_create(
                            name=pos_group
                        )

                        position, created = Positions.objects.get_or_create(
                            name=pos.strip(),
                        )
                        position.group = position_group
                        position.save()
                        # player.position.add(positions)
                        player_obj.position.add(position.id)
                        player_obj.save()
                player_obj.save()

                print("{} added successfully".format(full_name))
                # if created:

                #     print("{} added successfully".format(full_name))
                # else:
                #     print(
                #         " '{}' Player already have in database".format(full_name))

            except Exception as e:
                print(full_name)
                print(e)
                print("Error Occurred")
