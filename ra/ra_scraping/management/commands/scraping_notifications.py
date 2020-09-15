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
                            PlayerType, PositionGroup, Positions, SchoolsVisit,FbsSchools)
import ast
import argparse
from notifications.models import Notifications
from ra_user.models import MyBoard,WatchList,User
#from .school_logo import school_logo_update

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

        for player_lis in data:
            #player_queryset = Player.objects.filter(full_name__iexact=player_lis[17])
            player_queryset = Player.objects.filter(priority=int(player_lis[17]))
            if len(player_queryset) > 0:

                player = player_queryset[0]
                print(player_lis[0])
                fbs_offers = player_lis[6]
                fbsoffers = None
            else:
                fbs_offers = None
            if fbs_offers:
                try:
                    res = ast.literal_eval(fbs_offers)
                    total_offers = len(res.items())
                    # if total_offers >= 1:
                    #     fbsoffers = FbsOffers.objects.create(
                    #         total=str(total_offers)
                    #     )
                    #school_logo_update(res)
                    list_obj = []
                    for items in res.items():
                        if items[1][0] != '':
                            list_obj.append(items[0])
                            list_obj.insert(1, items[1][0])
                        # print(list_obj)
                        # try:
                        #     school = School.objects.get(
                        #         name=school_name.strip(),
                        #     )
                        #     #fbsoffers.schools.add(school)
                        # except School.DoesNotExist:
                        #     school = School.objects.create(
                        #         name=school_name.strip(),
                        #     )
                        #     #fbsoffers.schools.add(school)

                        # if school_logo:
                        #     img_url = school_logo
                        #     ssl._create_default_https_context = ssl._create_unverified_context
                        #     result = urllib2.urlretrieve(img_url)
                        #     school.logo.save(
                        #         os.path.basename(img_url),
                        #         File(open(result[0], 'rb'))
                        #     )
                        #     school.save()
                    visit_raw = player_lis[16]
                    school_visits = ''
                    if visit_raw is not '' and visit_raw is not None:
                        visit_res = ast.literal_eval(visit_raw)
                        school_visits = tuple(visit_res)
                except Exception as e:
                    print(e)
                try:
                    fbs_schools = tuple(res)
                    if len(fbs_schools) > 0  or len(list_obj) > 0:
                        if player.fbs_offers:
                            fbs_obj = FbsOffers.objects.get(id=player.fbs_offers.id)
                            if len(fbs_schools) > 0:
                                try:
                                    if player.fbs_offers.total != None:
                                        existing_offer_total = int(player.fbs_offers.total)
                                        put_offer_total = len(fbs_schools)
                                        if put_offer_total != existing_offer_total:
                                            existing_schools = list(
                                                player.fbs_offers.schools.all().values_list('name', flat=True))
                                            for fbs_school in existing_schools:
                                                if fbs_school not in fbs_schools:
                                                    try:
                                                        school_ob = School.objects.filter(
                                                            name__iexact=fbs_school)
                                                        if school_ob:
                                                            school_ob = school_ob[0]
                                                        else:
                                                            school_ob = School.objects.create(
                                                                name=fbs_school.title())
                                                    except Exception as e:
                                                        print(e)
                                                    delete_fbs_sch = FbsSchools.objects.filter(
                                                        fbs_offer=fbs_obj,
                                                        school=school_ob
                                                    ).delete()
                                            for new_fbs in fbs_schools:
                                                updated_existing_schools = list(
                                                    player.fbs_offers.schools.all().values_list('name', flat=True))
                                                if new_fbs not in updated_existing_schools:
                                                    school_ob = School.objects.filter(
                                                        name__iexact=new_fbs)
                                                    if school_ob:
                                                        new_school_obj = school_ob[0]
                                                    else:
                                                        new_school_obj = School.objects.create(
                                                            name=new_fbs.title())
                                                    try:
                                                        adding_fbs_sch = FbsSchools.objects.get(
                                                            fbs_offer=fbs_obj,
                                                            school=new_school_obj,
                                                        )
                                                        adding_fbs_sch.status = 'old'
                                                        adding_fbs_sch.save()
                                                    except FbsSchools.DoesNotExist:
                                                        adding_fbs_sch = FbsSchools.objects.create(
                                                            fbs_offer=fbs_obj,
                                                            school=new_school_obj,
                                                            status="old"
                                                        )
                                            fbs_obj.total = str(put_offer_total)
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                        else:
                                            if put_offer_total == existing_offer_total:
                                                existing_schools = list(
                                                    player.fbs_offers.schools.all().values_list('name', flat=True))
                                                for fbs_school in existing_schools:
                                                    if fbs_school not in fbs_schools:
                                                        try:
                                                            school_ob = School.objects.filter(
                                                                name__iexact=fbs_school)
                                                            if school_ob:
                                                                school_ob = school_ob[0]
                                                            else:
                                                                school_ob = School.objects.create(
                                                                    name=fbs_school.title())
                                                        except Exception as e:
                                                            print(e)
                                                        delete_fbs_sch = FbsSchools.objects.filter(
                                                            fbs_offer=fbs_obj,
                                                            school=school_ob
                                                        ).delete()
                                                for new_fbs in fbs_schools:
                                                    updated_existing_schools = list(
                                                        player.fbs_offers.schools.all().values_list('name', flat=True))
                                                    if new_fbs not in updated_existing_schools:
                                                        try:
                                                            school_ob = School.objects.filter(
                                                                name__iexact=new_fbs)
                                                            if school_ob:
                                                                new_school_obj = school_ob[0]
                                                            else:
                                                                new_school_obj = School.objects.create(
                                                                    name=new_fbs.title())
                                                        except Exception as e:
                                                            print(e)

                                                        adding_fbs_sch = FbsSchools.objects.create(
                                                            fbs_offer=fbs_obj,
                                                            school=new_school_obj
                                                        )
                                                fbs_obj.total = str(put_offer_total)
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                    else:
                                        fbs_obj = FbsOffers.objects.create(
                                            total=str(len(fbs_schools)))
                                        fbs_schools_objs = School.objects.filter(
                                            name__in=fbs_schools)
                                        for school_obj in fbs_schools_objs:
                                            try:
                                                fbs_school_obj = FbsSchools.objects.get(
                                                    fbs_offer=fbs_obj,
                                                    school=school_obj,
                                                )
                                                fbs_school_obj.status = 'old'
                                                fbs_school_obj.save()
                                            except FbsSchools.DoesNotExist:
                                                fbs_school_obj = FbsSchools.objects.create(
                                                    fbs_offer=fbs_obj,
                                                    school=school_obj,
                                                    status='old'
                                                )

                                        fbs_obj.total = str(len(fbs_schools))
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                except Exception as e:
                                    print(e)
                            if len(list_obj) > 0:
                                commit_school = list_obj[0]
                                commit_date = list_obj[1]
                                if player.fbs_offers.hard_commit != None:
                                    hard_commit_obj = FbsHardCommit.objects.get(
                                        id=player.fbs_offers.hard_commit.id)
                                    if commit_school != None:
                                        hard_commit_school_obj = School.objects.filter(
                                            name__iexact=commit_school)
                                        if hard_commit_school_obj:
                                            hard_commit_school_obj = hard_commit_school_obj[0]
                                        else:
                                            hard_commit_school_obj = School.objects.create(
                                            name=commit_school)
                                        if commit_date != None:
                                            hard_commit_school_obj.commited_on = commit_date
                                            hard_commit_school_obj.save()
                                            fbs_obj.hard_commit = hard_commit_school_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                    else:
                                        hard_commit_school_obj.school = None
                                        hard_commit_school_obj.commited_on = None
                                        hard_commit_school_obj.save()
                                        fbs_obj.hard_commit = hard_commit_school_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                else:
                                    hard_commit_school_obj = None
                                    if commit_school != None and commit_school != '':
                                        # try:
                                        #     hard_commit_sch = School.objects.filter(
                                        #         name__iexact=commit_school)[0]
                                        # except School.DoesNotExist:
                                        #     hard_commit_sch = School.objects.create(
                                        #         name=commit_school)
                                        try:
                                            school_ob = School.objects.filter(
                                                name__iexact=commit_school)
                                            if school_ob:
                                                hard_commit_sch = school_ob[0]
                                            else:
                                                hard_commit_sch = School.objects.create(
                                                    name=commit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if hard_commit_sch != None:
                                            hard_commit_school_obj = FbsHardCommit.objects.create(
                                                school=hard_commit_sch)
                                            if commit_date != None:
                                                hard_commit_school_obj.commited_on = commit_date
                                                hard_commit_school_obj.save()
                                                fbs_obj.hard_commit = hard_commit_school_obj
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj

                                            else:
                                                if fbs_obj != None:
                                                    fbs_obj.hard_commit = None
                                                    fbs_obj.save()
                                                    player.fbs_offers = fbs_obj
                            else:
                                if player.fbs_offers.hard_commit:
                                    hard_commit_school_obj = FbsHardCommit.objects.get(
                                            id=player.fbs_offers.hard_commit.id)
                                    if hard_commit_school_obj != None:
                                        hard_commit_school_obj = None
                                        #hard_commit_obj.save()
                                        if fbs_obj != None:
                                            fbs_obj.hard_commit = hard_commit_school_obj
                                            fbs_obj.save()

                            if len(school_visits) > 0:
                                try:
                                    #if player.fbs_offers.school_visits:
                                    if player.fbs_offers.visits != None:
                                        schools_objs = School.objects.filter(
                                            name__in=school_visits)
                                        visit_obj = SchoolsVisit.objects.get(
                                            id=player.fbs_offers.visits.id)
                                        visit_obj.schools.clear()
                                        visit_obj.total = None
                                        visit_obj.save()
                                        if len(schools_objs) > 0:
                                            for school_obj in schools_objs:
                                                visit_obj.schools.add(
                                                    school_obj.id)
                                            visit_obj.total = str(len(schools_objs))
                                            visit_obj.save()
                                            fbs_obj.visits = visit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                            #player.save()
                                        else:
                                            visit_obj.total = None
                                            fbs_obj.visits = visit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                            #player.save()
                                    else:
                                        if len(school_visits) > 0:
                                            visit_obj = SchoolsVisit.objects.create(
                                                total=str(len(school_visits)))
                                            visit_schools_objs = School.objects.filter(
                                                name__in=school_visits)
                                            for school_obj in visit_schools_objs:
                                                visit_obj.schools.add(
                                                    school_obj.id)
                                            visit_obj.save()
                                            fbs_obj.visits = visit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                except Exception as e:
                                    print(e)
                            else:
                                if player.fbs_offers.visits:
                                    visit_obj = SchoolsVisit.objects.get(
                                            id=player.fbs_offers.visits.id)
                                    if visit_obj != None:
                                        visit_obj = None
                                        #hard_commit_obj.save()
                                        player.fbs_offers.visits = visit_obj
                        else:
                            fbs_obj = None
                            hard_commit_obj = None
                            visits_obj = None
                            if len(fbs_schools) >= 1:
                                fbs_obj = FbsOffers.objects.create(
                                    total=str(len(fbs_schools)))
                                fbs_schools_objs = School.objects.filter(
                                    name__in=fbs_schools)
                                for school_obj in fbs_schools_objs:
                                    try:
                                        fbs_school_obj = FbsSchools.objects.get(
                                            fbs_offer=fbs_obj,
                                            school=school_obj,
                                        )
                                        fbs_school_obj.status = 'old'
                                        fbs_school_obj.save()
                                    except FbsSchools.DoesNotExist:
                                        fbs_school_obj = FbsSchools.objects.create(
                                            fbs_offer=fbs_obj,
                                            school=school_obj,
                                            status='old'
                                        )

                                fbs_obj.total = str(len(fbs_schools))
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj
                                # notifications_count = len(fbs_schools)
                            if len(list_obj) > 0:
                                commit_school = list_obj[0]
                                commit_date = list_obj[1]
                                hard_commit_sch = None
                                # try:
                                #     if commit_school != None:
                                #         hard_commit_sch = School.objects.filter(
                                #             name__iexact=commit_school)[0]
                                # except School.DoesNotExist:
                                #     if commit_school != None:
                                #         hard_commit_sch = School.objects.create(
                                #             name=commit_school)
                                try:
                                    school_ob = School.objects.filter(
                                        name__iexact=commit_school)
                                    if school_ob:
                                        hard_commit_sch = school_ob[0]
                                    else:
                                        hard_commit_sch = School.objects.create(
                                            name=commit_school.title())
                                except Exception as e:
                                    print(e)           
                                # if commit_school != None:
                                if hard_commit_sch != None:
                                    hard_commit_obj = FbsHardCommit.objects.create(
                                        school=hard_commit_sch)
                                    if commit_date != None:
                                        hard_commit_obj.commited_on = commit_date
                                        hard_commit_obj.save()
                                        if fbs_obj != None:
                                            fbs_obj.hard_commit = hard_commit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                        else:
                                            fbs_obj = FbsOffers.objects.create(
                                                hard_commit=hard_commit_obj)
                                            fbs_obj.hard_commit = hard_commit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                else:
                                    if fbs_obj != None:
                                        fbs_obj.hard_commit = None
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj


                            if len(school_visits) >= 1:
                                visit_schools_objs = School.objects.filter(
                                    name__in=school_visits)[0]
                                # if fbs_obj == None:
                                visits_obj = SchoolsVisit.objects.create(
                                    total=str(len(school_visits)))
                                visit_schools_objs = School.objects.filter(
                                    name__in=school_visits)
                                for school_obj in visit_schools_objs:
                                    visits_obj.schools.add(school_obj.id)
                                visits_obj.save()
                                if fbs_obj != None:
                                    fbs_obj.visits = visits_obj
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj

                                else:
                                    fbs_obj = FbsOffers.objects.create(
                                        visits=visits_obj)
                                    player.fbs_offers = fbs_obj
                            else:
                                if fbs_obj != None:
                                    fbs_obj.visits = None
                                    player.fbs_offers = fbs_obj
                        player.save()

                except Exception as e:
                    print(e)
