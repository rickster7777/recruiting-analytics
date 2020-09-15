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
            try:
                full_name = player[0].strip().replace(',', '')
                rank_val = player[18]
                if rank_val != None and rank_val != '':
                    rank_no = int(rank_val)
                else:
                    rank_no = None
                first_name = player[0].split()[0].strip().replace(',', '')
                if len(player[0].split()) >= 3:
                    last_name = player[0].split()[1].strip(
                    ).replace(',', '') + " " + player[0].split()[2].upper().replace(',', '')
                else:
                    last_name = player[0].split()[1].strip().title().replace(',', '')
                state_name = player[1]
                city_name = player[2]
                high_school = player[3].replace('  ', ' ').strip()
                positions = player[4]
                if positions != None and positions != '':
                    positions = positions.split(',')
                else:
                    positions = []
                rating = player[5]
                if rating:
                    if rating is not '':
                        star = int(rating)
                    else:
                        star = None
                else:
                    star = None
                # if rating:
                #     star = int(rating)
                # else:
                #     star = None
                p_height = player[7]
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
                if yr is not '':
                    yr = int(yr)
                    yr = re.sub(r"[^0-9]", "", str(yr))
                    cls_year, created = Classification.objects.get_or_create(
                        year=str(yr)
                    )
                else:
                    cls_year = None
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
                try:
                    update_player = Player.objects.get(
                        full_name__iexact=full_name.strip(),
                        city__name__iexact=city_name.strip(),
                        state__abbreviation__iexact=state_name.strip(),
                        school__name__iexact=high_school.strip(),
                        classification__year__iexact=cls_year.year
                    )
                    update_player.first_name=first_name.title().strip()
                    update_player.last_name=last_name.title().strip()
                    update_player.vertical=vertical
                    update_player.rank = rank_no
                    update_player.star_rating = star
                    update_player.position.clear()
                    update_player.short_shuttle = short_shuttle
                    update_player.fourty_yard_dash = forty
                    update_player.twitter_handle = twitter_handle
                    if p_height != None and p_height != '':
                        p_height = str(p_height)
                        if len(p_height) == 1:
                            feet = int(p_height)
                            inches = 0
                            player_height = (feet*12 + inches)
                            update_player.height = player_height
                        else:
                            if len(p_height) >= 3:
                                list_obj = p_height.split('.')
                                feet = int(list_obj[0])
                            if len(list_obj) >= 2:
                                inches = int(list_obj[1])
                            else:
                                inches = 0
                            player_height = (feet*12 + inches)
                            update_player.height = player_height


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
                        get_school = School.objects.filter(
                            name__iexact=high_school.title().strip()
                        )
                        if get_school:
                            get_school = get_school[0]
                            update_player.school = get_school
                        else:
                            school = School.objects.create(
                                name=high_school.title().strip(),
                            )
                            update_player.school = school
                    # if fbsoffers is not None:
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
                        update_player.position.clear()
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
                            update_player.position.add(position.id)
                    update_player.save()
                    print(update_player.full_name + "has been updated...")
                except Player.DoesNotExist:
                    add_player = Player.objects.create(
                        full_name=full_name.title().strip(),
                    )
                    add_player.first_name = first_name.title().strip()
                    add_player.last_name = last_name.title().strip()
                    add_player.twitter_handle = twitter_handle
                    add_player.fourty_yard_dash = forty
                    add_player.short_shuttle = short_shuttle
                    add_player.vertical = vertical
                    add_player.priority = priority
                    add_player.star_rating = star
                    add_player.rank = rank_no

                    if p_height != None and p_height != '':
                        p_height = str(p_height)
                        if len(p_height) == 1:
                            feet = int(p_height)
                            inches = 0
                            player_height = (feet*12 + inches)
                            add_player.height = player_height
                        else:
                            if len(p_height) >= 3:
                                list_obj = p_height.split('.')
                                feet = int(list_obj[0])
                            if len(list_obj) >= 2:
                                inches = int(list_obj[1])
                            else:
                                inches = 0
                            player_height = (feet*12 + inches)
                            add_player.height = player_height

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
                    if yr is not '':
                        yr = int(yr)
                        yr = re.sub(r"[^0-9]", "", str(yr))
                        year, created = Classification.objects.get_or_create(
                            year=str(yr)
                        )
                        add_player.classification = year

                    if jersey_no is not '':
                        add_player.jersey_number = int(jersey_no)
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
                            add_player.position.add(position.id)
                    add_player.save()
                    print(add_player.full_name + "has been added...")
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)