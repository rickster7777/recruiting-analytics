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
                            PlayerType, PositionGroup, Positions, SchoolsVisit, FbsSchools)
import ast
import argparse


class Command(BaseCommand):
    """
        Use Case: python manage.py update
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/import_players.xlsx
    """
    help = 'Used for Importing Players Data from Excel File.'

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
        for player in data:
            try:
                full_name = player[0].strip().replace(',', '')
                state_name = player[1]
                city_name = player[2]
                high_school = player[3].replace('  ', ' ').strip()
                yr = player[12]

                existing_player = Player.objects.filter(full_name__iexact=full_name)
                flag = ''
                if existing_player:
                    #if existing_player[0].state.abbreviation:
                    if (existing_player[0].state.abbreviation == state_name) and (existing_player[0].city.name == city_name) and (existing_player[0].school.name == high_school):
                        continue
                    else:
                        flag = 'create new player'

                    # existing_player[0].city.name
                    # existing_player[0].school.name
                    # existing_player[0].classification.year
                if (len(existing_player) == 0) or (flag != ''):
                    first_name = player[0].split()[0].strip()
                    if len(player[0].split()) >= 3:
                        last_name = player[0].split()[1].strip(
                        ) + " " + player[0].split()[2].upper()
                    else:
                        last_name = player[0].split()[1].strip().title() 
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
                    twitter_handle = player[14]
                    if twitter_handle is not '':
                        twitter_handle = player[14].strip()
                    else:
                        twitter_handle = None

                    height = player[7]
                    weight = player[8]
                    jersey_no = player[13]
                    avatar = player[15]
                    positions = player[4]
                    rating = player[5]
                    if rating:
                        if rating is not '':
                            star = int(rating)
                        else:
                            star = None
                    else:
                        star = None
                    if positions != None and positions != '':
                        positions = positions.split(',')
                    else:
                        positions = []

                    new_player = Player.objects.create(
                        full_name=full_name.title().strip(),
                        first_name=first_name.title().strip(),
                        last_name=last_name.title().strip(),
                        twitter_handle=twitter_handle,
                        fourty_yard_dash=forty,
                        short_shuttle=short_shuttle,
                        vertical=vertical,
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
                                    abbreviation=state_name.strip().upper()
                                )
                            except State.DoesNotExist:
                                state_obj = State.objects.create(
                                    abbreviation=state_name.strip().upper()
                                )
                        new_player.state = state_obj

                    if city_name != None and city_name != '':
                        try:
                            city_obj = City.objects.get(
                                name__iexact=city_name.strip().title(),
                                state=state_obj
                            )
                            new_player.city = city_obj
                        except City.DoesNotExist:
                            try:
                                city_obj = City.objects.get(
                                    name__iexact=city_name.strip().title()
                                )
                            except City.DoesNotExist:
                                city_obj = City.objects.create(
                                    name=city_name.strip().title()
                                )
                            new_player.city = city_obj
                    if high_school != None and high_school != '':
                        try:
                            get_school = School.objects.get(
                                name__iexact=high_school.title().strip()
                            )
                            new_player.school = get_school
                        except School.DoesNotExist:
                            school = School.objects.create(
                                name=high_school.title().strip(),
                            )
                            new_player.school = school
                    try:
                        if avatar:
                            img_url = avatar
                            ssl._create_default_https_context = ssl._create_unverified_context
                            result = urllib2.urlretrieve(img_url)
                            new_player.profile_photo.save(
                                os.path.basename(
                                    new_player.first_name + '-'
                                    + new_player.last_name + '.png'),
                                File(open(result[0], 'rb'))
                            )
                        else:
                            new_player.profile_photo = None
                            new_player.save()
                    except Exception as e:
                        new_player.profile_photo = None
                        new_player.save()
                        print("{} Player Avatar not found in given URL {}".format(
                            full_name, e))
                    if yr is not '':
                        yr = int(yr)
                        yr = re.sub(r"[^0-9]", "", str(yr))
                        year, created = Classification.objects.get_or_create(
                            year=str(yr)
                        )
                        new_player.classification = year
                    if jersey_no:
                        if jersey_no is not '':
                            new_player.jersey_number = int(jersey_no)

                    if height is not '':
                        new_player.height = float(height)

                    if weight is not '':
                        new_player.weight = float(weight)
                                        
                    new_player.star_rating = star

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
                            new_player.position.add(position.id)
                    new_player.save()
                    visit_raw = player[16]
                    school_visit = None
                    if visit_raw:
                        if visit_raw is not ('') or ("{}"):
                            visit_res = ast.literal_eval(visit_raw)
                            total_visits = len(visit_res.items())

                            if total_visits >= 1:
                                school_visit = SchoolsVisit.objects.create(
                                    total=str(total_visits)
                                )
                                for items in visit_res.items():
                                    school_name = items[0]
                                    if type(items[1]) == tuple:
                                        school_logo = items[1][0]
                                    else:
                                        school_logo = items[1]

                                    school = School.objects.filter(
                                        name=school_name.strip(),
                                    )
                                    if school:
                                        if school_logo:
                                            img_url = school_logo
                                            ssl._create_default_https_context = ssl._create_unverified_context
                                            result = urllib2.urlretrieve(
                                                img_url)
                                            school[0].logo.save(
                                                os.path.basename(img_url),
                                                File(open(result[0], 'rb'))
                                            )
                                            school[0].save()
                                            school_visit.schools.add(school[0])
                                    else:
                                        school = School.objects.create(
                                            name=school_name.strip(),
                                        )
                                        if school_logo:
                                            img_url = school_logo
                                            ssl._create_default_https_context = ssl._create_unverified_context
                                            result = urllib2.urlretrieve(
                                                img_url)
                                            school.logo.save(
                                                os.path.basename(img_url),
                                                File(open(result[0], 'rb'))
                                            )
                                            school.save()
                                            school_visit.schools.add(school)
                                tot = school_visit.schools.all().count()
                                school_visit.total = tot
                                school_visit.save()
                    fbs_offers = player[6]
                    fbsoffers = None
                    if fbs_offers:
                        try:
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
                                    school_name = items[0]
                                    if list_obj[1] is not '':
                                        commited_date = list_obj[1].strip()
                                    else:
                                        commited_date = None
                                    if len(list_obj) >= 4:
                                        school_logo = list_obj[3]
                                    else:
                                        school_logo = list_obj[2]
                                    try:
                                        school_obj = School.objects.get(
                                            name__iexact=school_name.strip(),
                                        )
                                        try:
                                            fbs_school_obj = FbsSchools.objects.get(
                                                fbs_offer=fbsoffers,
                                                school=school_obj
                                            )
                                        except FbsSchools.DoesNotExist:
                                            fbs_school_obj = FbsSchools.objects.create(
                                                fbs_offer=fbsoffers,
                                                school=school_obj
                                            )

                                    except School.DoesNotExist:
                                        school_obj = School.objects.create(
                                            name=school_name.strip(),
                                        )
                                        try:
                                            FbsSchools.objects.get(
                                                fbs_offer=fbs_offers,
                                                school=school_obj
                                            )
                                        except FbsSchools.DoesNotExist:
                                            fbs_school_obj = FbsSchools.objects.create(
                                                fbs_offer=fbs_offers,
                                                school=school_obj
                                            )
                                    if school_logo:
                                        try:
                                            img_url = school_logo
                                            ssl._create_default_https_context = ssl._create_unverified_context
                                            result = urllib2.urlretrieve(img_url)
                                            school_obj.logo.save(
                                                os.path.basename(img_url),
                                                File(open(result[0], 'rb'))
                                            )
                                            school_obj.save()
                                        except Exception as e:
                                            print(e)
                                    if list_obj[1] is not '':
                                        try:
                                            fbs_hard_commit = FbsHardCommit.objects.get(
                                                school=school_obj,
                                                commited_on=list_obj[1].strip()
                                            )
                                            fbsoffers.hard_commit = fbs_hard_commit
                                        except FbsHardCommit.DoesNotExist:
                                            fbs_hard_commit = FbsHardCommit.objects.create(
                                                school=school_obj,
                                                commited_on=list_obj[1].strip()
                                            )
                                            fbsoffers.hard_commit = fbs_hard_commit
                                if school_visit:
                                    fbsoffers.visits = school_visit
                                totl = fbsoffers.schools.all().count()
                                fbsoffers.total = totl
                                fbsoffers.save()
                        except Exception as e:
                            print(e)
                    try:
                        if fbsoffers is not None:
                            new_player.fbs_offers = fbsoffers
                        new_player.save()
                    except Exception as e:
                        print(e)
                   
            except Exception as e:
                print(e)