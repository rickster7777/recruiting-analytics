import io
import json
import os.path
import re
import urllib.request as urllib2
from django.conf import settings
import xlrd
import csv
from django.core.files import File
from django.core.management.base import BaseCommand
import ssl
from address.models import City, School, State, Country
from players.models import (Classification, FbsHardCommit, FbsOffers, Player,
                            PlayerType, PositionGroup, Positions, SchoolsVisit)
import ast
import argparse


class Command(BaseCommand):
    """
        Use Case: python manage.py update
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/import_players.xlsx
    """
    help = 'Used to Importing Players Data from Excel File.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        # parser.add_argument('csvfile', nargs='?', type=argparse.FileType('r'))

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
        # Deliting ll schools
        # School.objects.all().delete()
        # PositionGroup.objects.all().delete()
        # Player.objects.all().delete()
        # Positions.objects.all().delete()
        # Classification.objects.all().delete()
        # School.objects.all().delete()
        # FbsHardCommit.objects.all().delete()
        # FbsOffers.objects.all().delete()
        # Positions.objects.all().delete()
        # PositionGroup.objects.all().delete()

        print("player has beed adding...")
        print(".........")
        for player in data:
            print(player[0])
            try:
                full_name = player[0].strip()

                first_name = player[0].split()[0].strip()
                if len(player[0].split()) >= 3:
                    last_name = player[0].split()[1].strip(
                    ) + " " + player[0].split()[2].upper()
                else:
                    last_name = player[0].split()[1].strip().title()
                state_name = player[1]
                city_name = player[2]
                high_school = player[3].replace('  ', ' ').strip()
                positions = player[4].split()
                rating = player[5]
                if rating:
                    if rating is not '':
                        star = int(rating)
                else:
                    star = None
                # if rating:
                #     star = int(rating)
                # else:
                #     star = None
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
                # visit_raw = player[16]
                # school_visit = None
                # if visit_raw:
                #     if visit_raw is not '':
                #         visit_res = ast.literal_eval(visit_raw)
                #         total_visits = len(visit_res.items())

                #         if total_visits >= 1:
                #             school_visit = SchoolsVisit.objects.create(
                #                 total=str(total_visits)
                #             )
                #             for items in visit_res.items():
                #                 school_name = items[0]
                #                 if type(items[1]) == tuple:
                #                     school_logo = items[1][0]
                #                 else:
                #                     school_logo = items[1]

                #                 school = School.objects.filter(
                #                     name=school_name.strip(),
                #                 )
                #                 if school:
                #                     if school_logo:
                #                         img_url = school_logo
                #                         ssl._create_default_https_context = ssl._create_unverified_context
                #                         result = urllib2.urlretrieve(
                #                             img_url)
                #                         school[0].logo.save(
                #                             os.path.basename(img_url),
                #                             File(open(result[0], 'rb'))
                #                         )
                #                         school[0].save()
                #                         school_visit.schools.add(school[0])
                #                 else:
                #                     school = School.objects.create(
                #                         name=school_name.strip(),
                #                     )
                #                     if school_logo:
                #                         img_url = school_logo
                #                         ssl._create_default_https_context = ssl._create_unverified_context
                #                         result = urllib2.urlretrieve(
                #                             img_url)
                #                         school.logo.save(
                #                             os.path.basename(img_url),
                #                             File(open(result[0], 'rb'))
                #                         )
                #                         school.save()
                #                         school_visit.schools.add(school)
                #             tot = school_visit.schools.all().count()
                #             school_visit.total = tot
                #             school_visit.save()
                # fbs_offers = player[6]
                # fbsoffers = None
                # if fbs_offers:
                #     try:
                #         res = ast.literal_eval(fbs_offers)
                #         total_offers = len(res.items())
                #         if total_offers >= 1:
                #             fbsoffers = FbsOffers.objects.create(
                #                 total=str(total_offers)
                #             )

                #             # res = ast.literal_eval(fbs_offers)
                #             # total_offers = len(res.items())
                #             for items in res.items():
                #                 list_obj = list(items[1])
                #                 list_obj.insert(0, items[0])
                #                 # print(list_obj)
                #                 school_name = items[0]
                #                 if list_obj[1] is not '':
                #                     commited_date = list_obj[1].strip()
                #                 else:
                #                     commited_date = None
                #                 if len(list_obj) >= 4:
                #                     school_logo = list_obj[3]
                #                 else:
                #                     school_logo = list_obj[2]
                #                 try:
                #                     school = School.objects.get(
                #                         name=school_name.strip(),
                #                     )
                #                     fbsoffers.schools.add(school)
                #                 except School.DoesNotExist:
                #                     school = School.objects.create(
                #                         name=school_name.strip(),
                #                     )
                #                     fbsoffers.schools.add(school)
                #                 else:
                #                     fbsoffers.schools.add(school)

                #                 if school_logo:
                #                     img_url = school_logo
                #                     ssl._create_default_https_context = ssl._create_unverified_context
                #                     result = urllib2.urlretrieve(img_url)
                #                     school.logo.save(
                #                         os.path.basename(img_url),
                #                         File(open(result[0], 'rb'))
                #                     )
                #                     school.save()
                #                 if list_obj[1] is not '':
                #                     try:
                #                         fbs_hard_commit = FbsHardCommit.objects.get(
                #                             school=school,
                #                             commited_on=list_obj[1].strip()
                #                         )
                #                         fbsoffers.hard_commit = fbs_hard_commit
                #                     except FbsHardCommit.DoesNotExist:
                #                         fbs_hard_commit = FbsHardCommit.objects.create(
                #                             school=school,
                #                             commited_on=list_obj[1].strip()
                #                         )
                #                         fbsoffers.hard_commit = fbs_hard_commit
                #             if school_visit:
                #                 fbsoffers.visits = school_visit
                #             totl = fbsoffers.schools.all().count()
                #             fbsoffers.total = totl
                #             fbsoffers.save()
                #     except Exception as e:
                #         print(e)
                try:
                    update_player = Player.objects.get(priority=priority)
                    update_player.star_rating = star
                    # update_player.position.all().delete()
                    update_player.position.clear()
                    update_player.vertical = vertical
                    update_player.short_shuttle = short_shuttle
                    update_player.fourty_yard_dash = forty
                    update_player.twitter_handle = twitter_handle
                    if state_name != None and state_name != '':
                        try:
                            country_obj = Country.objects.get(name='USA')
                            state_obj = State.objects.get(
                                abbreviation__iexact=state_name.strip().upper(),
                                country=country_obj
                            )
                            state_obj.country = country_obj
                            state_obj.save()
                        except State.DoesNotExist:
                            try:
                                state_obj = State.objects.get(
                                    abbreviation=state_name.strip().upper()
                                )
                            except State.DoesNotExist:
                                state_obj = State.objects.create(
                                    abbreviation=state_name.strip().upper()
                                )
                        update_player.state = state_obj

                    if city_name != None and city_name != '':
                        try:
                            city_obj = City.objects.get(
                                name__iexact=city_name.strip().title(),
                                state=state_obj
                            )
                            update_player.city = city_obj
                        except City.DoesNotExist:
                            try:
                                city_obj = City.objects.get(
                                    name__iexact=city_name.strip().title()
                                )
                            except City.DoesNotExist:
                                city_obj = City.objects.create(
                                    name=city_name.strip().title()
                                )
                            update_player.city = city_obj
                    if high_school != None and high_school != '':
                        try:
                            get_school = School.objects.get(
                                name__iexact=high_school.title().strip()
                            )
                            update_player.school = get_school
                        except School.DoesNotExist:
                            school = School.objects.create(
                                name=high_school.title().strip(),
                            )
                            update_player.school = school
                    # if fbsoffers is not None:
                    #     update_player.fbs_offers = fbsoffers
                    try:
                        if avatar:
                            img_url = avatar
                            ssl._create_default_https_context = ssl._create_unverified_context
                            result = urllib2.urlretrieve(img_url)
                            # image_name = img_url.split('/')[-1]
                            update_player.profile_photo.save(
                                os.path.basename(
                                    update_player.first_name + '-'
                                    + update_player.last_name + '.png'),
                                File(open(result[0], 'rb'))
                            )
                        else:
                            update_player.profile_photo = None
                            update_player.save()
                    except Exception as e:
                        update_player.profile_photo = None
                        update_player.save()
                        print("{} Player Avatar not found in given URL {}".format(
                            full_name, e))
                    if yr is not '':
                        yr = int(yr)
                        yr = re.sub(r"[^0-9]", "", str(yr))
                        year, created = Classification.objects.get_or_create(
                            year=str(yr)
                        )
                        update_player.classification = year
                    if jersey_no:
                        if jersey_no is not '':
                            update_player.jersey_number = int(jersey_no)

                    # if height is not '':
                    #     update_player.height = float(height)

                    if weight is not '':
                        update_player.weight = float(weight)
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
                            try:
                                position_group = PositionGroup.objects.get(
                                    name=pos_group
                                )
                            except PositionGroup.DoesNotExist:
                                position_group = PositionGroup.objects.create(
                                    name=pos_group
                                )
                            try:

                                position = Positions.objects.get(
                                    name=pos.strip(),
                                )
                                position.group = position_group
                                position.save()
                            except Positions.DoesNotExist:
                                position = Positions.objects.create(
                                    name=pos.strip(),
                                )
                                position.group = position_group
                                position.save()

                            # player.position.add(positions)
                            update_player.position.add(position.id)
                    update_player.save()
                except Player.DoesNotExist:
                    add_player = Player.objects.create(
                        full_name=full_name.title().strip(),
                        first_name=first_name.title().strip(),
                        last_name=last_name.title().strip(),
                        twitter_handle=twitter_handle,
                        fourty_yard_dash=forty,
                        short_shuttle=short_shuttle,
                        vertical=vertical,
                        priority=priority
                    )
                    if state_name != None and state_name != '':
                        try:
                            country_obj = Country.objects.get(name='USA')
                            state_obj = State.objects.get(
                                abbreviation__iexact=state_name.strip().upper(),
                                country=country_obj
                            )
                            state_obj.country = country_obj
                            state_obj.save()
                        except State.DoesNotExist:
                            try:
                                state_obj = State.objects.get(
                                    abbreviation__iexact=state_name.strip().upper()
                                )
                            except State.DoesNotExist:
                                state_obj = State.objects.create(
                                    abbreviation=state_name.strip().upper()
                                )

                        add_player.state = state_obj

                    if city_name != None and city_name != '':
                        try:
                            city_obj = City.objects.get(
                                name__iexact=city_name.strip().title(),
                                state=state_obj
                            )
                        except City.DoesNotExist:
                            try:
                                city_obj = City.objects.get(
                                    name__iexact=city_name.strip().title()
                                )
                            except City.DoesNotExist:
                                city_obj = City.objects.create(
                                    name=city_name.strip().title()
                                )
                        add_player.city = city_obj
                    if high_school != None and high_school != '':
                        try:
                            get_school = School.objects.get(
                                name__iexact=high_school.title().strip()
                            )
                            add_player.school = get_school
                        except School.DoesNotExist:
                            school = School.objects.create(
                                name=high_school.title().strip(),
                            )
                            add_player.school = school
                    # if fbsoffers is not None:
                    #     add_player.fbs_offers = fbsoffers
                    add_player.position.clear()
                    player_role = PlayerType.objects.get(
                        name='prospect'
                    )
                    add_player.role = player_role
                    if high_school:
                        highschool, created = School.objects.get_or_create(
                            name=high_school.title().strip(),
                        )
                        add_player.school = highschool
                    # if fbs_offers:
                    #     add_player.fbs_offers = fbsoffers
                    try:
                        if avatar:
                            img_url = avatar
                            ssl._create_default_https_context = ssl._create_unverified_context
                            result = urllib2.urlretrieve(img_url)
                            # image_name = img_url.split('/')[-1]
                            add_player.profile_photo.save(
                                os.path.basename(
                                    player.first_name + '-'
                                    + player.last_name + '.png'),
                                File(open(result[0], 'rb'))
                            )
                    except Exception as e:
                        print("{} Player Avatar not found in given URL {}".format(
                            full_name, e))
                    if yr is not '':
                        yr = int(yr)
                        yr = re.sub(r"[^0-9]", "", str(yr))
                        year, created = Classification.objects.get_or_create(
                            year=str(yr)
                        )
                        add_player.classification = year

                    if jersey_no is not '':
                        add_player.jersey_number = int(jersey_no)
                    # if height is not '':
                    #     update_player.height = float(height)
                    if weight is not '':
                        add_player.weight = float(weight)
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
                            #add_player.fbs_offers = fbsoffers
                            add_player.position.add(position.id)
                    add_player.save()

                    print('player doesnot exists', full_name)
                except Exception as e:
                    print(e)
                    print('error found')
                    # update_player = Player.objects.create(
                    #     full_name=full_name.title().strip(),
                    #     first_name=first_name.title().strip(),
                    #     last_name=last_name.title().strip(),
                    #     twitter_handle=twitter_handle,
                    #     fourty_yard_dash=forty,
                    #     short_shuttle=short_shuttle,
                    #     vertical=vertical,
                    #     priority=priority
                    # )
                    # update_player.position = None
                    # if state_name:
                    #     state, created = State.objects.get_or_create(
                    #         abbreviation=state_name.strip()
                    #     )
                    #     update_player.state = state
                    # if city_name:
                    #     city, created = City.objects.get_or_create(
                    #         name=city_name.strip(),
                    #         state=state
                    #     )
                    #     update_player.city = city
                    # player_role = PlayerType.objects.get(
                    #     name='prospect'
                    # )
                    # update_player.role = player_role
                    # if high_school:
                    #     highschool, created = School.objects.get_or_create(
                    #         name=high_school.title().strip(),
                    #     )
                    #     update_player.school = highschool
                    # if fbs_offers:
                    #     update_player.fbs_offers = fbsoffers
                    # try:
                    #     if avatar:
                    #         img_url = avatar
                    #         ssl._create_default_https_context = ssl._create_unverified_context
                    #         result = urllib2.urlretrieve(img_url)
                    #         # image_name = img_url.split('/')[-1]
                    #         update_player.profile_photo.save(
                    #             os.path.basename(img_url),
                    #             File(open(result[0], 'rb'))
                    #         )
                    # except Exception as e:
                    #     print("{} Player Avatar not found in given URL {}".format(
                    #         full_name, e))
                    # if yr is not '':
                    #     yr = int(yr)
                    #     yr = re.sub(r"[^0-9]", "", str(yr))
                    #     year, created = Classification.objects.get_or_create(
                    #         year=str(yr)
                    #     )
                    #     update_player.classification = year

                    # if jersey_no is not '':
                    #     update_player.jersey_number = int(jersey_no)
                    # if height is not '':
                    #     update_player.height = float(height)
                    # if weight is not '':
                    #     update_player.weight = float(weight)
                    # if len(positions) > 0:
                    #     for pos in positions:
                    #         db = ['CB', 'S', 'SS', 'FS', 'DB']
                    #         rb = ['APB', 'RB', 'FB']
                    #         rec = ['WR', 'TE', 'R', 'T']
                    #         ol = ['OL', 'OT', 'OG', 'OC']
                    #         dl = ['DL', 'WDE', 'SDE', 'DT']
                    #         lb = ['LB', 'ILB', 'OLB']
                    #         qb = ['Pro', 'PRO', 'Dual', 'DUAL', 'QB']
                    #         Special = ['ATH', 'K', 'P', 'LS', 'RET']

                    #         pos = re.sub(r"[^a-zA-Z]", "", pos.upper())
                    #         if pos in db:
                    #             pos_group = 'DB'
                    #         elif pos in rb:
                    #             pos_group = 'RB'
                    #         elif pos in rec:
                    #             pos_group = 'R'
                    #         elif pos in ol:
                    #             pos_group = 'OL'
                    #         elif pos in dl:
                    #             pos_group = 'DL'
                    #         elif pos in lb:
                    #             pos_group = 'LB'
                    #         elif pos in qb:
                    #             pos_group = 'QB'
                    #         elif pos in Special:
                    #             pos_group = 'Special'
                    #         else:
                    #             pos_group = None

                    #         position_group, created = PositionGroup.objects.get_or_create(
                    #             name=pos_group
                    #         )

                    #         position, created = Positions.objects.get_or_create(
                    #             name=pos.strip(),
                    #         )
                    #         position.group = position_group
                    #         position.save()
                    #         update_player.position.add(position.id)
                    # update_player.save()

            except Exception as e:
                print(e)
                print(e)
                print("Error Occurred")
