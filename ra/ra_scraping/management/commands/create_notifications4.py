import io
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import csv
import time
import re
import os
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import concurrent.futures
import time
from datetime import datetime
from players.models import Player, FbsSchools,FbsOffers, SchoolsVisit, FbsHardCommit,FbsDeCommit
from address.models import School
import ssl
import urllib.request as urllib2
from django.core.files import File
from notifications.models import Notifications
from ra_user.models import MyBoard,WatchList,User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}


class Command(BaseCommand):
    """
        Use Case: python manage.py create_notifications4
    """
    help = 'Used for getting notifications update.'

    def handle(self, *args, **options):
        div_3 = 3*int(Player.objects.all().exclude(role__name__iexact='nfl').count()/5)
        div_4 = 4*int(Player.objects.all().exclude(role__name__iexact='nfl').count()/5)
        player_info= Player.objects.filter(priority__range=[div_3 + 1 ,div_4]).order_by('priority')
        def get_driver():
            try:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--incognito")
                chrome_options.add_argument("disk-cache-size=0")
                chrome_options.add_argument("--disable-browser-cache-memory")
                chrome_options.add_argument("--disable-browser-cache-disk")
                chrome_options.add_argument("--disable-browser-cache-offline")
                chrome_options.add_argument("--disable-browser-cache-disk-enable")
                chrome_options.add_argument("--disable-cache-offline-enable")
                chrome_options.add_argument("--disable-network-http-use-cache")
                chrome_options.add_argument("--disable-dev-shm-usage")
                driver = webdriver.Chrome(options=chrome_options)
                return driver
            except Exception as e:
                print("{}".format(e))
        driver = get_driver()
        for player in player_info:
            try:
                school_lis = []
                city_lis = []
                states_lis = []

                rivals_offer_dict = {}
                offers_rivals = []
                rivals_visit_dict = {}
                visits_rivals = []
                rivals_hard_commit = ()
                rivals_decommit = ()
                nrivals_driver_exception = ''


                #Seven
                seven_driver_exception = ''
                offers_seven = []
                visits_seven = []
                seven_hard_commit = ()
                seven_offer_dict = {}
                seven_visit_dict = {}
                names = player.full_name
                a = names.split()
                print(a[0],a[1])
                if player.classification:
                    classif = player.classification.year
                else:
                    classif = '2021'

                if player.school and player.school.name:
                    school_lis.append(player.school.name)
                else:
                    school_lis.append('')

                if player.city and player.city.name:
                    city_lis.append(player.city.name)
                else:
                    city_lis.append('')    

                if player.state and player.state.abbreviation:
                    states_lis.append(player.state.abbreviation)
                else:
                    states_lis.append('')
                try:
                    url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2021,%22page_number%22:1,%22page_size%22:50%7D'.format(
                    a[0], a[1])

                    if classif == '2020':
                        url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2020,%22page_number%22:1,%22page_size%22:50%7D'.format(
                        a[0],a[1])
                    elif classif == '2022':
                        url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2022,%22page_number%22:1,%22page_size%22:50%7D'.format(a[0],a[1])
                    nrivals_driver_exception = ''
                    try:
                        driver.get(url)
                    except UnboundLocalError as error:
                        #print(error)
                        nrivals_driver_exception = 'raised'
                    if nrivals_driver_exception != 'raised':
                        delay = 4
                        nrivals_flag = ''
                        try:
                            WebDriverWait(driver, delay).until(
                                EC.presence_of_element_located((By.ID, 'content_')))
                            print("Page is ready!")
                        except TimeoutException:
                            print("Loading took too much time!")
                            nrivals_flag ="Player Not Found"
                            driver.delete_all_cookies()
                            pass
                        if nrivals_flag != "Player Not Found":
                            html = driver.page_source
                            driver.delete_all_cookies()
                            soup = BeautifulSoup(html, 'html.parser')
                            name_link = soup.find('div', {'class': 'name-star ng-scope'})
                            profile_link = name_link.find('a', href=True).get('href')

                            profile_in = requests.get(profile_link)
                            nrv_soup = BeautifulSoup(profile_in.content, 'html.parser')
                            if nrv_soup.find('div', {'class': 'prospect-full-name'}):
                                pl_name = nrv_soup.find('div', {'class': 'prospect-full-name'})
                                FN_LN = pl_name.text.replace('\n', '').replace('\t', '')
                                if a[0].lower().strip() and a[1].lower().strip() not in FN_LN.lower().strip():
                                    pass
                                else:
                                    #print(profile_link)

                                    if nrv_soup.find('div', {'class': 'small-mobile-vitals'}):
                                        info = nrv_soup.find(
                                            'div', {'class': 'small-mobile-vitals'})
                                        if info.findAll('div', {'class': 'vital-line vital-line-location'}):
                                            state_school = info.findAll(
                                                'div', {'class': 'vital-line vital-line-location'})
                                            state_city = state_school[0].text
                                            st = state_city.split(',')
                                            state = st[1].strip()
                                            city = st[0].strip()
                                            school = state_school[1].text.strip()
                                        else:
                                            state = ''
                                            city = ''
                                            school = ''
                                        if state.lower().strip() in states_lis[-1].lower().strip() or city.lower().strip() in city_lis[-1].lower().strip() or school.lower().strip() in school_lis[-1].lower().strip():
                                            try:
                                                if nrv_soup.find('div', {'class': 'logo-box-flex'}):
                                                    comit_link = nrv_soup.find(
                                                        'div', {'class': 'logo-box-flex'}).find('img').get('ng-src')
                                                else:
                                                    comit_link = ''
                                                if nrv_soup.find('div', {'class': 'date'}):
                                                    comit_date = nrv_soup.find(
                                                        'div', {'class': 'date'}).text.replace('Committed ', '')
                                                else:
                                                    comit_date = ''
                                                if nrv_soup.find('a', {'class': 'college'}):
                                                    comit_state_name = nrv_soup.find(
                                                        'a', {'class': 'college'}).text
                                                else:
                                                    comit_state_name = ''
                                                if comit_state_name != '' and comit_date != '':
                                                    rivals_hard_commit = comit_state_name, comit_date, comit_link
                                                decommit_date = ''
                                                decommit_state = ''
                                                try:
                                                    if nrv_soup.find('div',{'class':'previous-commit-text'}):
                                                        if nrv_soup.find('div',{'class':'previous-commit-text'}).find('span'):
                                                            previous_date = nrv_soup.find('div',{'class':'previous-commit-text'}).find('span').text
                                                            if '-' in previous_date:
                                                                dates_splitting = previous_date.split('-')
                                                                if len(dates_splitting) > 0:
                                                                    comit_date = dates_splitting[0].strip()
                                                                else:
                                                                    comit_date = ''
                                                                if len(dates_splitting) > 1:
                                                                    decommit_date = dates_splitting[1].strip()
                                                                else:
                                                                    decommit_date = ''    
                                                            else:
                                                                comit_date = ''
                                                                decommit_date = ''
                                                        if nrv_soup.find('div',{'class':'previous-commit-text'}).find('a'):
                                                            decommit_state = nrv_soup.find('div',{'class':'previous-commit-text'}).find('a').text
                                                        if comit_state_name != '' and comit_date != '':
                                                            commit_date_obj = datetime.strptime(comit_date, '%m/%d/%Y')
                                                            decommit_date_obj = datetime.strptime(decommit_date, '%m/%d/%Y')
                                                            present = datetime.now()
                                                            if decommit_date_obj < present:
                                                                comit_date = ''
                                                            elif decommit_date_obj > present:
                                                                decommit_date = ''
                                                except Exception as e:
                                                    print(e)

                                                        #date_object = datetime.strptime(comit_date, '%m/%d/%Y').date()
                                                if len(rivals_hard_commit) == 0:
                                                    if comit_state_name != '' and comit_date != '':
                                                        rivals_hard_commit = comit_state_name, comit_date, comit_link
                                                if decommit_state != '' and decommit_date != '':
                                                    rivals_decommit = decommit_state,decommit_date
                                                    
                                            except Exception as e:
                                                print(e)
                                                print('In hard commit')

                                            driver.get(profile_link)
                                            offers_list = driver.page_source
                                            ofsoup = BeautifulSoup(offers_list, 'html.parser')

                                            state_lis = ofsoup.find_all('td', {'class': 'school'})
                                            school_offer = ofsoup.find_all('td', {'class': 'offer'})
                                            school_logos = ofsoup.find_all('div', {'class': 'img-container'})

                                            offers_rivals = []
                                            try:
                                                for states, offers, img in zip(state_lis, school_offer, school_logos):
                                                    if img.find('img'):
                                                        school_logo = img.find('img').get('src')
                                                    if states.find('a', href=True):
                                                        st = states.find('a', href=True).text
                                                    if offers:
                                                        of = offers.text
                                                        if "—" in of:
                                                            of = "No"
                                                        else:
                                                            of = "Yes"
                                                        if of == 'Yes':
                                                            st_of = st, '', school_logo
                                                            offers_rivals.append(st_of)
                                                if len(offers_rivals) > 0:
                                                    if len(rivals_hard_commit) > 0 and type((offers_rivals[0][0])) == str:
                                                        try:
                                                            for tup_obj in offers_rivals:
                                                                if tup_obj[0] == rivals_hard_commit[0]:
                                                                    lis_obj = list(tup_obj)
                                                                    lis_obj[1] = rivals_hard_commit[1]
                                                                    tup = tuple(lis_obj)
                                                                    for n, i in enumerate(offers_rivals):
                                                                        if i[0] == tup[0]:
                                                                            offers_rivals[n] = tup
                                                        except Exception as e:
                                                            print(e)
                                                            print("In tup obj" )            
                                                            
                                                    if type((offers_rivals[0][0])) == str:            
                                                        rivals_offer_dict = {sublist[0]: sublist[1:] for sublist in offers_rivals}            
                                            except Exception as e:
                                                print(e)
                                            ofsoup.find_all('div', {'class': 'date ng-binding'})
                                            vis_date = ofsoup.find_all('td', {'class': 'visit ng-scope'})
                                            visits_rivals = []
                                            try:
                                                for states, img, vis in zip(state_lis, school_logos, vis_date):
                                                    if img.find('img'):
                                                        school_logo = img.find('img').get('src')
                                                        if states.find('a', href=True):
                                                            st = states.find(
                                                                'a', href=True).text
                                                        if vis.find('div', {'class': 'date ng-binding'}):

                                                            st_vis = st, school_logo
                                                            visits_rivals.append(st_vis)
                                                        elif vis.find('div', {'class': 'date ng-binding official'}):
                                                            #visd = vis.find('div',{'class':'date ng-binding official'}).text.replace('\n','')
                                                            st_vis = st, school_logo
                                                            visits_rivals.append(st_vis)
                                                rivals_visit_dict = {sublist[0]: sublist[1:] for sublist in visits_rivals}
                                            except Exception as e:
                                                print(e)

                                            #print(a, 'nrv')
                                            driver.delete_all_cookies()
                                        else:
                                            rivals_offer_dict = {}
                                            rivals_visit_dict = {}
                                            rivals_hard_commit = ''
                                            pass

                                    else:
                                        pass
                                        print('School,City,State unmatched')
                except Exception as e:
                    pass
                try:
                    if len(a) == 3:
                        url = 'https://247sports.com/Season/{}-Football/Recruits/?&Player.FullName={}%20{}%20{}'.format(
                            classif, a[0].lower(), a[1].lower(),a[2].lower())
                    else:
                        url = 'https://247sports.com/Season/{}-Football/Recruits/?&Player.FullName={}%20{}'.format(
                            classif, a[0], a[1])
                    try:
                        time.sleep(2)
                        driver.get(url)
                        #break
                    except UnboundLocalError as error:
                        seven_driver_exception = 'raised'
                    except Exception as e:
                        print(e)
                    if seven_driver_exception != 'raised':
                        try:
                            WebDriverWait(driver, 4).until(EC.presence_of_element_located(
                                (By.XPATH, '/html/body/section/section/div/section[2]/section/section/section/div/div[1]/ul[2]/li/ul/li[2]/a')))
                            print("247sports.com Page is ready!")
                        except TimeoutException:
                            print("Not in 247sports.com!")

                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        name_link = soup.findAll('ul', {'class': 'player'})
                        if len(name_link) > 0:
                            b = name_link[0].find('a').get('href')
                            results = soup.find('ul', {'class': 'results'})
                            if len(results.text) == 0:
                                driver.delete_all_cookies()
                                #driver.quit()
                                pass
                            elif 'No results found.' in results.text:
                                driver.delete_all_cookies()
                                #driver.quit()
                                pass
                            else:
                                profile_link = requests.get(b, headers=HEADERS)
                                profile_soup = BeautifulSoup(
                                    profile_link.content, 'html.parser')
                                if profile_soup.find_all('ul', {"class": "details"}):
                                    High_school = profile_soup.find_all(
                                        'ul', {"class": "details"})
                                    school_city_class = High_school[0].find_all('li')
                                    try:
                                        if len(school_city_class) > 0:
                                            school = ''
                                            state = ''
                                            city = ''
                                            for scl in school_city_class:
                                                if 'High School' in scl.text:
                                                    school = scl.text.replace(
                                                        ' High School  ', '').strip()
                                                if 'Home Town' in scl.text:
                                                    state_city = scl.text.replace(
                                                        ' Home Town ', '')
                                                    st = state_city.split(',')
                                                    state = st[1].strip()
                                                    city = st[0].strip()
                                    except Exception as e:
                                        print(e)
                                else:
                                    school = ''
                                    state = ''
                                    city = ''
                                # position height and weight
                                try:
                                    if profile_soup.find('section',{'class':'as-a-prospect'}):
                                        commit_school_name = ''
                                        if profile_soup.find('section',{'class':'bottom'}):
                                            commit_school_name = profile_soup.find('section',{'class':'bottom'}).find('header').find('h2').text.strip()

                                        if profile_soup.find('ul',{"class":"commitment"}):
                                            commit_date_list = profile_soup.find('ul',{"class":"commitment"}).find_all('li')
                                            for commited_date in commit_date_list:
                                                if 'Committed' in commited_date.text:
                                                    commit_date = commited_date.text.replace('Committed','').strip()
                                                if commited_date.find('img'):
                                                    commit_school_logo = commited_date.find('img').get('data-src')
                                                    commit_school_logo = commit_school_logo.split('?')[0]

                                        if commit_school_name != '' and commit_date != '' and commit_school_logo != '':
                                            seven_hard_commit = (commit_school_name,commit_date,commit_school_logo)
                                except Exception as e:
                                    print(e)
                                offers_seven = []
                                visits_seven = []
                                #driver.quit()
                                if state.lower().strip() in states_lis[-1].lower().strip() or city.lower().strip() in city_lis[-1].lower().strip() or school.lower().strip() in school_lis[-1].lower().strip():
                                    print(a[0]+" "+a[1], 'match')
                                    # request_TL = None
                                    # recruiting_profile_soup = None
                                    if profile_soup.find('section',{'class':'as-a-prospect'}):
                                        footer_section = profile_soup.find('section',{'class':'as-a-prospect'}).find('div',{'class':'footer'})
                                        #recruting profile link
                                        view_recruiting_profile_link = footer_section.find('a').get('href')
                                        request_profile_page = requests.get(view_recruiting_profile_link, headers=HEADERS)
                                        recruiting_profile_soup = BeautifulSoup(request_profile_page.content,'html.parser')
                                        #college link
                                        team_list = recruiting_profile_soup.find('a', {'class': 'college-comp__view-all'})
                                        team_list_link = team_list.get('href')
                                        request_TL = requests.get(team_list_link, headers=HEADERS)

                                    else:
                                        if profile_soup.find('a', {'class': 'college-comp__view-all'}):
                                            team_list = profile_soup.find('a', {'class': 'college-comp__view-all'})
                                            team_list_link = team_list.get('href')
                                            request_TL = requests.get(team_list_link, headers=HEADERS)

                                    #requesting without Selenium
                                    TL_soup = BeautifulSoup(request_TL.content, 'html.parser')
                                    state_list = TL_soup.findAll('div', {'class': 'first_blk'})
                                    Offers_list = TL_soup.findAll('div', {'class': 'secondary_blk'})
                                    Image_logo = TL_soup.findAll('img', {'class': 'jsonly'})

                                    for states, offers, logo in zip(state_list, Offers_list, Image_logo):
                                        LOGO = logo.get('data-src').split('?')[0]
                                        state_date = states.find_all('a')
                                        st = state_date[0].text.strip()
                                        date = state_date[1].text.strip().replace(
                                            '(', '').replace(')', '')
                                        if 'Edit' in date:
                                            date = ''
                                        of = offers.find('span', {'class': 'offer'}).text.replace(
                                            ' Offer: ', '').strip()
                                        if of == 'Yes':
                                            st_of = st, date, LOGO
                                            offers_seven.append(st_of)
                                        if date != '' and len(seven_hard_commit) == 0:
                                            seven_hard_commit = (st, date, LOGO)
                                        visit_counts = offers.find(
                                            'span', {'class': 'visit'}).text
                                        if ' Visit:  -  ' in visit_counts:
                                            pass
                                        else:
                                            vis_st = st, LOGO
                                            visits_seven.append(vis_st)

                                    seven_offer_dict = {sublist[0]: sublist[1:] for sublist in offers_seven}
                                    seven_visit_dict = {sublist[0]: sublist[1:] for sublist in visits_seven}
                                else:
                                    seven_offer_dict = {}
                                    seven_visit_dict = {}
                                    seven_hard_commit = ''
                        else:
                            pass
                            #driver.quit()
                    else:
                        pass
                        #driver.quit()
                except Exception as e:
                    print(e)
                    driver.quit()
                    driver = get_driver()
                    time.sleep(5)
                    continue
                #Database update and Notification Checker
                #driver.quit()
                try:
                    school_logo_lis = []
                    fbs_schools = []
                    if len(seven_offer_dict) > 0:
                        fbs_schools = tuple(seven_offer_dict)
                        for key,value in seven_offer_dict.items():
                            school_logo_lis.append(value[1])

                    else:
                        if len(rivals_offer_dict) > 0:
                            fbs_schools = tuple(rivals_offer_dict)
                            for key,value in rivals_offer_dict.items():
                                school_logo_lis.append(value[1])

                    school_visits = []
                    if len(seven_visit_dict) > 0:
                        school_visits = tuple(seven_visit_dict)
                    else:
                        if len(rivals_visit_dict):
                            school_visits = tuple(rivals_visit_dict)

                    hard_commit_tuple = ()

                    if len(seven_hard_commit) > 0:
                        hard_commit_tuple  = seven_hard_commit
                    else:
                        if len(rivals_hard_commit) > 0:
                            hard_commit_tuple = rivals_hard_commit


                    if len(hard_commit_tuple) > 0:
                        commit_school = hard_commit_tuple[0]
                        commit_date = hard_commit_tuple[1]
                    if len(rivals_decommit) > 0:
                        decommit_school = rivals_decommit[0]
                        decommit_date = rivals_decommit[1]
                except Exception as e:
                    print(e)
                if nrivals_driver_exception != 'raised' or seven_driver_exception != 'raised':
                    fbs_schools = [sch.lower().strip() for sch in fbs_schools]
                    try:
                        notifications_total_offer_checker = ''
                        notification_schools_offer_checker= ''
                        notification_hard_commit_school = ''
                        notification_hard_commit_date = ''
                        notification_decommit_school = ''
                        notification_decommit_date = ''
                        add_count = []
                        #fbs_schools = tuple(res)
                        #if len(fbs_schools) > 0  or len(hard_commit_tuple) > 0:
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
                                                if fbs_school.lower().strip() not in fbs_schools:
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
                                                    notification_schools_offer_checker = 'raised'
                                            for new_fbs in fbs_schools:
                                                updated_existing_schools = list(
                                                    player.fbs_offers.schools.all().values_list('name', flat=True))
                                                updated_existing_schools = [sch.lower().strip() for sch in updated_existing_schools]
                                                if new_fbs not in updated_existing_schools:
                                                    try:
                                                        new_school_obj = School.objects.filter(
                                                            name__iexact=new_fbs)
                                                        if new_school_obj:
                                                            new_school_obj = new_school_obj[0]
                                                        else:
                                                            new_school_obj = School.objects.create(
                                                                name=new_fbs.title())
                                                    except Exception as e:
                                                        print(e)
                                                    adding_fbs_sch = FbsSchools.objects.create(
                                                        fbs_offer=fbs_obj,
                                                        school=new_school_obj,
                                                        status="new"
                                                    )
                                                    notifications_total_offer_checker = 'raised'
                                                    add_count.append('added')
                                            fbs_obj.total = str(put_offer_total)
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                        else:
                                            if put_offer_total == existing_offer_total:
                                                existing_schools = list(
                                                    player.fbs_offers.schools.all().values_list('name', flat=True))
                                                existing_schools = [sch.lower().strip() for sch in existing_schools]
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
                                                        notification_schools_offer_checker = 'raised'
                                                for new_fbs in fbs_schools:
                                                    updated_existing_schools = list(
                                                        player.fbs_offers.schools.all().values_list('name', flat=True))
                                                    updated_existing_schools = [sch.lower().strip() for sch in existing_schools]
                                                    if new_fbs not in updated_existing_schools:
                                                        try:
                                                            new_school_obj = School.objects.filter(
                                                                name__iexact=new_fbs)
                                                            if new_school_obj:
                                                                new_school_obj = new_school_obj[0]
                                                            else:
                                                                new_school_obj = School.objects.create(
                                                                    name=new_fbs.title())
                                                        except Exception as e:
                                                            print(e)

                                                        adding_fbs_sch = FbsSchools.objects.create(
                                                            fbs_offer=fbs_obj,
                                                            school=new_school_obj,
                                                            status="new"
                                                        )
                                                        notification_schools_offer_checker = 'raised'
                                                        add_count.append('added')
                                                fbs_obj.total = str(put_offer_total)
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                    else:
                                        fbs_obj = FbsOffers.objects.create(
                                            total=str(len(fbs_schools)))
                                        fbs_schools_objs = []
                                        for school_object in fbs_schools:
                                            try:
                                                school_object_lis = School.objects.filter(name__iexact=school_object)
                                                if school_object_lis:
                                                    fbs_schools_objs.append(school_object_lis[0])
                                                else:
                                                    new_school_object = School.objects.create(name=school_object.title())
                                                    fbs_schools_objs.append(new_school_object)   

                                            # fbs_schools_objs = School.objects.filter(
                                            #     name__in=fbs_schools)
                                            except Exception as e:
                                                print(e)
                                        for school_obj in fbs_schools_objs:
                                            try:
                                                fbs_school_obj = FbsSchools.objects.get(
                                                    fbs_offer=fbs_obj,
                                                    school=school_obj
                                                )
                                            except FbsSchools.DoesNotExist:
                                                fbs_school_obj = FbsSchools.objects.create(
                                                    fbs_offer=fbs_obj,
                                                    school=school_obj,
                                                    status='new'
                                                )

                                        fbs_obj.total = str(len(fbs_schools))
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                        #notifications_count = len(fbs_schools)
                                        for fbs_s in fbs_schools:
                                            add_count.append(fbs_s)
                                        notifications_total_offer_checker = 'raiseD'

                                except Exception as e:
                                    print(e)
                            else:
                                if fbs_obj:
                                    fbs_obj.total = None
                                    if len(fbs_obj.schools.all()) > 0:
                                        notification_schools_offer_checker == 'raised'
                                    fbs_obj.schools.clear()
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                            if len(hard_commit_tuple) > 0:
                                if player.fbs_offers.hard_commit != None:
                                    hard_commit_obj = FbsHardCommit.objects.get(
                                        id=player.fbs_offers.hard_commit.id)
                                    if commit_school != None:
                                        try:
                                            hard_commit_school_obj = School.objects.filter(
                                                name__iexact=commit_school)
                                            if hard_commit_school_obj:
                                                hard_commit_school_obj = hard_commit_school_obj[0]
                                            else:
                                                hard_commit_school_obj = School.objects.create(
                                                    name=commit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if hard_commit_obj.school:
                                            if hard_commit_obj.school.name != None and  hard_commit_school_obj.name != None:
                                                if hard_commit_obj.school.name.lower().strip() == hard_commit_school_obj.name.lower().strip():
                                                    notification_hard_commit_school = 'unraised'
                                                else:
                                                    notification_hard_commit_school = 'raised'

                                        if commit_date != None and hard_commit_obj.commited_on != None:
                                            if commit_date.strip() == hard_commit_obj.commited_on.strip():
                                                notification_hard_commit_date = 'unraised'
                                            else:
                                                notification_hard_commit_date = 'raised'

                                        hard_commit_sch = None
                                        try:
                                            hard_commit_sch = School.objects.filter(
                                                name__iexact=commit_school)
                                            if hard_commit_sch:
                                                hard_commit_sch = hard_commit_sch[0]
                                            else:
                                                hard_commit_sch = School.objects.create(
                                                    name=commit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if hard_commit_sch != None:
                                            hard_commit_obj.school = hard_commit_sch
                                            # hard_commit_obj = FbsHardCommit.objects.create(
                                            #     school=hard_commit_sch)
                                            if commit_date != None:
                                                hard_commit_obj.commited_on = commit_date
                                                hard_commit_obj.save()
                                                fbs_obj.hard_commit = hard_commit_obj
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                    else:
                                        hard_commit_obj.school = None
                                        hard_commit_obj.commited_on = None
                                        hard_commit_obj.save()
                                        fbs_obj.hard_commit = hard_commit_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                else:
                                    hard_commit_obj = None
                                    if commit_school != None and commit_school != '':
                                        try:
                                            hard_commit_sch = School.objects.filter(
                                                name__iexact=commit_school)
                                            if hard_commit_sch:
                                                hard_commit_sch = hard_commit_sch[0]
                                            else:
                                                hard_commit_sch = School.objects.create(
                                                    name=commit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if hard_commit_sch != None:
                                            hard_commit_obj = FbsHardCommit.objects.create(
                                                school=hard_commit_sch)
                                            notification_hard_commit_school = 'raised'
                                            if commit_date != None:
                                                hard_commit_obj.commited_on = commit_date
                                                hard_commit_obj.save()
                                                fbs_obj.hard_commit = hard_commit_obj
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                                notification_hard_commit_date = 'raised'

                                            else:
                                                if fbs_obj != None:
                                                    fbs_obj.hard_commit = None
                                                    fbs_obj.save()
                                                    player.fbs_offers = fbs_obj
                            else:
                                # if player.fbs_offers.hard_commit:
                                #     notification_hard_commit_date = 'raised'
                                if fbs_obj != None:
                                    if fbs_obj.hard_commit:
                                        notification_hard_commit_date = 'raised'
                                    fbs_obj.hard_commit = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
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
                                            visit_obj.save()
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
                                except Exception as e:
                                    print(e)
                            else:
                                if fbs_obj != None:
                                    fbs_obj.visits = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                            if len(rivals_decommit) > 0:
                                if player.fbs_offers.decommit != None:
                                    decommit_obj = FbsDeCommit.objects.get(
                                        id=player.fbs_offers.decommit.id)
                                    if decommit_school != None:
                                        try:
                                            decommit_school_obj = School.objects.filter(
                                                name__iexact=decommit_school)
                                            if decommit_school_obj:
                                                decommit_school_obj = decommit_school_obj[0]
                                            else:
                                                decommit_school_obj = School.objects.create(
                                                    name=decommit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if decommit_obj.school:
                                            if decommit_obj.school.name != None and  decommit_school_obj.name != None:
                                                if decommit_obj.school.name.lower().strip() == decommit_school_obj.name.lower().strip():
                                                    notification_decommit_school = 'unraised'
                                                else:
                                                    notification_decommit_school = 'raised'

                                        if decommit_date != None and decommit_obj.decommited_on != None:
                                            if decommit_date.strip() == decommit_obj.decommited_on.strip():
                                                notification_decommit_date = 'unraised'
                                            else:
                                                notification_decommit_date = 'raised'

                                        decommit_sch = None
                                        try:
                                            decommit_sch = School.objects.filter(
                                                name__iexact=decommit_school)
                                            if decommit_sch:
                                                decommit_sch = decommit_sch[0]
                                            else:
                                                decommit_sch = School.objects.create(
                                                    name=decommit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if decommit_sch != None:
                                            decommit_obj.school = decommit_sch
                                            if decommit_date != None:
                                                decommit_obj.decommited_on = decommit_date
                                                decommit_obj.save()
                                                fbs_obj.decommit = decommit_obj
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                    else:
                                        decommit_obj.school = None
                                        decommit_obj.decommited_on  = None
                                        decommit_obj.save()
                                        fbs_obj.decommit = decommit_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                else:
                                    decommit_obj = None
                                    if decommit_school != None and decommit_school != '':
                                        try:
                                            decommit_sch = School.objects.filter(
                                                name__iexact=decommit_school)
                                            if decommit_sch:
                                                decommit_sch = decommit_sch[0]
                                            else:
                                                decommit_sch = School.objects.create(
                                                    name=decommit_school.title())
                                        except Exception as e:
                                            print(e)
                                        if decommit_sch != None:
                                            decommit_obj = FbsDeCommit.objects.create(
                                                school=decommit_sch)
                                            #notification_decommit_school = 'raised'
                                            if decommit_date != None:
                                                decommit_obj.decommited_on = decommit_date
                                                decommit_obj.save()
                                                fbs_obj.decommit = decommit_obj
                                                fbs_obj.save()
                                                player.fbs_offers = fbs_obj
                                                notification_decommit_date = 'raised'

                                            else:
                                                if fbs_obj != None:
                                                    fbs_obj.decommit = None
                                                    fbs_obj.save()
                                                    player.fbs_offers = fbs_obj
                            else:
                                if fbs_obj != None:
                                    if fbs_obj.decommit:
                                        notification_decommit_date = 'raised'
                                    fbs_obj.decommit = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj    

                        else:
                            fbs_obj = None
                            hard_commit_obj = None
                            visits_obj = None
                            if len(fbs_schools) >= 1:
                                fbs_obj = FbsOffers.objects.create(
                                    total=str(len(fbs_schools))
                                    )


                                fbs_schools_objs = School.objects.filter(
                                    name__in=fbs_schools)
                                for school_obj in fbs_schools_objs:
                                    try:
                                        fbs_school_obj = FbsSchools.objects.get(
                                            fbs_offer=fbs_obj,
                                            school=school_obj
                                        )
                                    except FbsSchools.DoesNotExist:
                                        fbs_school_obj = FbsSchools.objects.create(
                                            fbs_offer=fbs_obj,
                                            school=school_obj,
                                            status='new'
                                        )

                                fbs_obj.total = str(len(fbs_schools))
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj
                                # notifications_count = len(fbs_schools)
                                for fbs_s in fbs_schools:
                                    add_count.append(fbs_s)
                                notifications_total_offer_checker = 'raiseD'
                            if len(hard_commit_tuple) > 0:
                                hard_commit_sch = None
                                try:
                                    if commit_school != None:
                                        hard_commit_sch = School.objects.filter(
                                            name__iexact=commit_school)
                                        if hard_commit_sch:
                                            hard_commit_sch = hard_commit_sch[0]
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
                                        notification_hard_commit_school = 'raiseD'
                                else:
                                    if fbs_obj != None:
                                        fbs_obj.hard_commit = None
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj

                            else:
                                if fbs_obj != None:
                                    fbs_obj.hard_commit = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                            if len(school_visits) >= 1:
                                # visit_schools_objs = School.objects.filter(
                                #     name__in=school_visits)[0]
                                # # if fbs_obj == None:
                                visits_obj = SchoolsVisit.objects.create(
                                    total=str(len(school_visits))
                                    )
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
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                            if len(rivals_decommit) > 0:
                                decommit_sch = None
                                try:
                                    if decommit_school != None:
                                        decommit_sch = School.objects.filter(
                                            name__iexact=decommit_school)
                                        if decommit_sch:
                                            decommit_sch = decommit_sch[0]
                                        else:
                                            decommit_sch = School.objects.create(
                                                name=decommit_school.title())
                                except Exception as e:
                                    print(e)
                                # if decommit_school != None:
                                if decommit_sch != None:
                                    decommit_obj = FbsDeCommit.objects.create(
                                        school=decommit_sch)
                                    if decommit_date != None:
                                        decommit_obj.decommited_on = decommit_date
                                        decommit_obj.save()
                                        if fbs_obj != None:
                                            fbs_obj.decommit = decommit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                        else:
                                            fbs_obj = FbsOffers.objects.create(
                                                decommit=decommit_obj)
                                            fbs_obj.decommit = decommit_obj
                                            fbs_obj.save()
                                            player.fbs_offers = fbs_obj
                                        notification_decommit_school = 'raised'
                                else:
                                    if fbs_obj != None:
                                        fbs_obj.decommit = None
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj

                            else:
                                if fbs_obj != None:
                                    fbs_obj.decommit = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                        player.save()
                        try:
                            if notifications_total_offer_checker == 'raised' or notification_schools_offer_checker == 'raised' or notifications_total_offer_checker == 'raiseD':
                                myboard_players = MyBoard.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                watchlist_players = WatchList.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                user_ids = []
                                for vals in myboard_players:
                                    user_ids.append(vals)
                                for vals in watchlist_players:
                                    user_ids.append(vals)

                                unique_user_id = []
                                unique_user_id = list(set(user_ids))

                                for request_user in unique_user_id:
                                    try:
                                        notification_user = User.objects.get(id=request_user)
                                        notification = Notifications.objects.create(
                                            user=notification_user)
                                        notification.notification_type = 'offers'
                                        notification.player = player
                                        if len(add_count) > 0:
                                            notification.message = "has {} offers added.".format(
                                                len(add_count))
                                            print(player.full_name,notification.message)
                                        else:
                                            notification.message = "has offers updated."
                                            print(player.full_name,notification.message)
                                        notification.save()
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
                        try:
                            if notification_hard_commit_date == 'raised' or notification_hard_commit_school == 'raised' or notification_hard_commit_school == 'raiseD':
                                myboard_players = MyBoard.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                watchlist_players = WatchList.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                user_ids = []
                                for vals in myboard_players:
                                    user_ids.append(vals)
                                for vals in watchlist_players:
                                    user_ids.append(vals)

                                unique_user_id = []
                                unique_user_id = list(set(user_ids))

                                for request_user in unique_user_id:
                                    try:
                                        notification_user = User.objects.get(id=request_user)
                                        notification = Notifications.objects.create(
                                            user=notification_user)
                                        notification.notification_type = 'commit'
                                        if notification_hard_commit_school == 'raiseD':
                                            notification.message = "has a Commitment update"
                                        notification.message = "has a Commitment update"
                                        print(player.full_name,notification.message)
                                        notification.player = player
                                        notification.save()
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
                        try:
                            if notification_decommit_school == 'raised' or  notification_decommit_date == 'raised':
                                myboard_players = MyBoard.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                watchlist_players = WatchList.objects.filter(
                                    player=player).values_list('user__id', flat=True)
                                user_ids = []
                                for vals in myboard_players:
                                    user_ids.append(vals)
                                for vals in watchlist_players:
                                    user_ids.append(vals)

                                unique_user_id = []
                                unique_user_id = list(set(user_ids))

                                for request_user in unique_user_id:
                                    try:
                                        notification_user = User.objects.get(id=request_user)
                                        notification = Notifications.objects.create(
                                            user=notification_user)
                                        notification.notification_type = 'decommit'
                                        notification.message = "has a Decommitment update"
                                        print(player.full_name,notification.message)
                                        notification.player = player
                                        notification.save()
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
        os.system("pgrep chrome | xargs kill -9")