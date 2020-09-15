import concurrent.futures
import csv
import io
import os
import os.path
import re
import ssl
import time
import urllib.request as urllib2
from datetime import datetime
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from address.models import School
from notifications.models import Notifications
from players.models import (FbsDeCommit, FbsHardCommit, FbsOffers, FbsSchools,
                            Player, SchoolsVisit, Positions)
from ra_user.models import MyBoard, User, WatchList
from social_engagement.models import SocialEngagement

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}


class Command(BaseCommand):
    """
        Use Case: python manage.py player_update5
    """
    help = 'Used to Update players attributes from maxpreps/Nrivals/247Sports'

    def handle(self, *args, **options):
        school_lis = []
        city_lis = []
        states_lis = []
        div_4 = 4*int(Player.objects.all().exclude(role__name__iexact='nfl').count()/5)
        div_5 = int(Player.objects.all().exclude(role__name__iexact='nfl').count())
        player_prior = Player.objects.filter(priority__range=[div_4 + 1 ,div_5]).order_by('priority')
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
        for player in player_prior:
            try:
                if player:
                    max_lis = ['','','','','','','','','','','','','','','','','']
                    nrv_lis = ['','','','','','','','','','','','','','','','','']
                    seven_lis = ['','','','','','','','','','','','','','','','','']
                    rivals_offer_dict = {}
                    offers_rivals = []
                    rivals_visit_dict = {}
                    visits_rivals = []
                    rivals_hard_commit = ()
                    rivals_decommit = ()
                    nrivals_driver_exception = ''
                    offers_seven = []
                    visits_seven = []
                    seven_hard_commit = ()
                    seven_offer_dict = {}
                    seven_visit_dict = {}
                    seven_driver_exception = ''
                    
                    names = player.full_name
                    print(names)
                    a = names.split()
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
                        if len(a) == 3:
                            LINK_MAX = 'https://www.maxpreps.com/search/default.aspx?type=athlete&search={}%20{}%20{}&state=&gendersport=boys,football'.format(a[0], a[1],a[2])
                        else:
                            LINK_MAX = 'https://www.maxpreps.com/search/default.aspx?type=athlete&search={}%20{}&state=&gendersport=boys,football'.format(a[0], a[1])
                        time.sleep(3)
                        URL = requests.get(LINK_MAX)
                        rank_soup = BeautifulSoup(URL.content, 'html.parser')
                        match_case = rank_soup.find_all('li',{'class': 'row result'})
                        for school_name in match_case:
                            if school_name.find('div',{'class':'school-name row-column-2'}).find('a'):
                                result_school = school_name.find('div',{'class':'school-name row-column-2'}).find('a').next
                                if  result_school.lower().strip() in school_lis[-1].lower().strip():
                                    link_max = school_name.find('div', {'class': 'athlete-name row-column-1'}).find('a',href = True).get('href')
                                    rq_profile = requests.get(link_max)
                                    profile_soup = BeautifulSoup(rq_profile.content, 'html.parser')
                                    points = profile_soup.findAll('div', {'class': 'athlete-attributes'})

                                    jersey = profile_soup.find_all('div', {'class': 'row'})

                                    H_school = jersey[0].find('span', {'class': 'school-name'}).text
                                    city = jersey[0].find('span', {'class': 'school-city'}).text
                                    state = jersey[0].find('span', {'class': 'school-state'}).text

                                    if points[0].find('span', {'class': 'height'}):
                                        height = points[0].find('span', {'class': 'height'}).text.replace(
                                            '"', '').replace('\'', '-').replace('-','.')
                                    else:
                                        height = ''


                                    if points[0].find('span', {'class': 'weight'}):
                                        wt = points[0].find('span', {'class': 'weight'}).text
                                        weight = wt.replace(' lbs','')
                                        if weight == '0':
                                            weight = ''
                                    else:
                                        weight = ''
                                    if points[0].find('span', {'class': 'graduation-year'}):
                                        pl_class = points[0].find('span', {'class': 'graduation-year'}).text.replace('Graduates in ', '')
                                        if 'Graduated in ' in pl_class:
                                            pl_class = pl_class.replace('Graduated in ','')
                                    else:
                                        pl_class = ''
                                    if len(jersey)>1:
                                        s = jersey[1].find('dl').text

                                        if (s.find('Jersey') != -1):
                                            temp = re.findall(r'\d+', s)
                                            number = temp[0]

                                        else:
                                            number = ''
                                    else:
                                        number = ''
                                    if len(jersey)>1:

                                        if ('Pos' or 'Position') in jersey[1].findAll('dt')[0].text:
                                            position = jersey[1].findAll('dd')[0].text
                                            res = ''.join([i for i in position if not i.isdigit()])
                                            post = res.replace('#', '')
                                            if 'Yes' in post:
                                                post = post.replace('Yes','')
                                            if post == '--':
                                                post = ''
                                        elif len(jersey[1].findAll('dt')) >=2:

                                            if (jersey[1].findAll('dt')[1].text) == 'Pos' or 'Position':
                                                position = jersey[1].findAll('dd')[1].text
                                                res = ''.join([i for i in position if not i.isdigit()])
                                                post = res.replace(',', '')
                                                if 'Yes' in post:
                                                    post = post.replace('Yes','')
                                                if post == '--':
                                                    post = ''


                                        else:
                                            post = ''
                                    else:
                                        post = ''

                                    American_football_pos = ('QB','RB','FB','WR','TE','OL','C','LG','RG','T','LT',
                                                    'LB','ILB','OLB','MLB','RT','K','KR','DL','DE','DT','NT','DB','CB','FS','S','SS','P','PR')

                                    if post != '':
                                        pos_break = post.split()[0].replace(',','')
                                        if  pos_break not in American_football_pos:
                                            post = 'DB'

                                        if len(post.split()) == 2:
                                            pos_break = post.split()[1].replace(',','')
                                            if pos_break not in American_football_pos:
                                                post = post+','+'DB'
                                        #q = post.split()
                                        if len(post.split()) == 3:
                                            pos_break = post.split()[2].replace(',','')
                                            if pos_break not in American_football_pos:
                                                post = post+','+'DB'
                                    else :
                                        post = ''


                                    if profile_soup.find('div',{'class':'athlete-photo'}).find('a').get('href'):
                                        Headshot_image = profile_soup.find('div',{'class':'athlete-photo'}).find('a').get('style').split('\"')[1]
                                    else:
                                        Headshot_image = ''

                                    break
                                else:                           
                                    height = ''
                                    number = ''
                                    weight = ''
                                    pl_class = ''
                                    Headshot_image = ''
                                    post = ''
                                    city = ''
                                    state = ''
                                    H_school = ''
                                    jersey = ''

                        rating = ''
                        forty = ''
                        shuttle = ''
                        vertical = ''
                        tweet = ''
                        offers = ''
                        visits = ''


                        if pl_class in ('2021','2020','2022'):
                            if len(a) == 3:
                                max_lis[0] = a[0]+" "+a[1]+" "+a[2]
                            else:
                                max_lis[0] = (a[0]+" "+a[1])
                            max_lis[1] = state
                            max_lis[2] = city
                            max_lis[3] = H_school
                            max_lis[4] = post
                            max_lis[5] = rating
                            max_lis[6] = offers
                            max_lis[7] = height
                            max_lis[8] = weight
                            max_lis[9] =  forty
                            max_lis[10] = shuttle
                            max_lis[11] = vertical
                            max_lis[12] = pl_class
                            if number != '':
                                max_lis[13] = int(number)
                            else:
                                max_lis[13] = number    
                            max_lis[14] = tweet
                            max_lis[15] = Headshot_image
                            max_lis[16] = visits



                            #return max_lis
                    except Exception as e :
                        print(e)
                        print('In maxpreps')
                    # try:
                    #     chrome_options = Options()
                    #     chrome_options.add_argument("--headless")
                    #     chrome_options.add_argument("--incognito")
                    #     chrome_options.add_argument("disk-cache-size=0")
                    #     chrome_options.add_argument("--disable-browser-cache-memory")
                    #     chrome_options.add_argument("--disable-browser-cache-disk")
                    #     chrome_options.add_argument("--disable-browser-cache-offline")
                    #     chrome_options.add_argument("--disable-browser-cache-disk-enable")
                    #     chrome_options.add_argument("--disable-cache-offline-enable")
                    #     chrome_options.add_argument("--disable-network-http-use-cache")
                    #     chrome_options.add_argument("--disable-dev-shm-usage")
                    #     driver = webdriver.Chrome(options=chrome_options)
                    # except Exception as e:
                    #     print("{} in chrome options import".format(e))

                    try:
                        url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2021,%22page_number%22:1,%22page_size%22:50%7D'.format(
                        a[0], a[1])

                        if classif == '2020':
                            url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2020,%22page_number%22:1,%22page_size%22:50%7D'.format(a[0],a[1])
                        elif classif == '2022':
                            url = 'https://n.rivals.com/search#?query={}%20{}&formValues=%7B%22sport%22:%22Football%22,%22recruit_year%22:2022,%22page_number%22:1,%22page_size%22:50%7D'.format(a[0],a[1])
                        nrivals_driver_exception = ''
                        try:
                            driver.get(url)
                        except UnboundLocalError as error:
                            nrivals_driver_exception = 'raised'
                        if nrivals_driver_exception != 'raised':
                            delay = 2
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
                                    #nrivals_flag = ''
                                    pl_name = nrv_soup.find('div', {'class': 'prospect-full-name'})
                                    FN_LN = pl_name.text.replace('\n', '').replace('\t', '')
                                    if a[0].lower() and a[1].lower() not in FN_LN.lower():
                                        nrivals_flag ="Player Not Found"
                                        pass
                                    else:
                                        print(profile_link)

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
                                                if info.find('div',{'class': 'vital-line lg-sm-mobile'}):
                                                    position = info.find('div',{'class': 'vital-line lg-sm-mobile'}).text.strip()
                                                    if position == 'Athlete':
                                                        position = 'ATH'
                                                    if position == 'Cornerback':
                                                        position = 'CB'
                                                    if position == 'All-purpose back':
                                                        position = 'APB'
                                                    if position == 'Wide Receiver':
                                                        position = 'WR'
                                                    if position == 'Running Back':
                                                        position = 'RB'
                                                    if position == 'Tight end':
                                                        position = 'TE'
                                                    if position == 'Safety':
                                                        position = 'S'
                                                    if position == 'Pro-style quarterback':
                                                        position = 'PRO'
                                                    if position == 'Dual-threat quarterback':
                                                        position = 'DUAL'
                                                    if position == 'Inside linebacker':
                                                        position = 'ILB'
                                                    if position == 'Strongside defensive end':
                                                        position = 'SDE'
                                                    if position == 'Offensive tackle':
                                                        position = 'OT'
                                                else:
                                                    position = ''
                                                if info.findAll('div',{'class': 'vital-line'}):
                                                    height_weight = info.findAll('div',{'class': 'vital-line'})
                                                    class_year = height_weight[3] .text.replace('CLASS OF ','')

                                                    ht = height_weight[2].text.split('|')[0]
                                                    height = ht.strip()[:-2].replace('\'','-').replace('-','.')
                                                    if height.replace('.', '').isdigit():
                                                        height = height
                                                    else:
                                                        height = ''
                                                    wt = height_weight[2] .text.split('|')[1].strip()
                                                    weight = wt.replace(' lbs','').replace('lbs','')
                                                else:
                                                    class_year = ''
                                                    height = ''
                                                    weight = ''
                                                if nrv_soup.find('div',{'class': 'prospect-large-stars'}):
                                                    star_rating = nrv_soup.find('div',{'class': 'prospect-large-stars'}).find('rv-stars').get('num-stars')
                                                    if star_rating  == '0':
                                                        star_rating = ''
                                                else:
                                                    star_rating = ''
                                                if nrv_soup.find('img',{"class" : "left-personal-information prospect-image"}):
                                                    headshot_image = nrv_soup.find('img',{"class" : "left-personal-information prospect-image"}).get('ng-src')
                                                    if headshot_image == 'https://cdn.rivals.com/production/assets/icons/icons_prospectprofile_avatar-f8b63a445cc9298d92203997366f1a6d36b7c02de68654d3af2229092416a6da.svg':
                                                        headshot_image = ''
                                                else:
                                                    headshot_image = ''


                                                # Committed date
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

                                                driver.delete_all_cookies()
                                            else:
                                                state = ''
                                                city = ''
                                                school = ''
                                                position = ''
                                                class_year = ''
                                                height = ''
                                                weight = ''
                                                star_rating = ''
                                                headshot_image = ''
                                                pass

                                        else:
                                            print('School,City,State unmatched')
                                            pass
                            forty = ''
                            shuttle = ''
                            vertical = ''
                            j_number = ''
                            tweet = ''
                            if nrivals_flag == "Player Not Found":
                                state = ''
                                city = ''
                                school = ''
                                position = ''
                                class_year = ''
                                height = ''
                                weight = ''
                                star_rating = ''
                                headshot_image = ''



                            nrv_lis[0] = a[0]+" "+a[1]
                            nrv_lis[1] = state
                            nrv_lis[2] = city
                            nrv_lis[3] = school
                            nrv_lis[4] = position
                            nrv_lis[5] = star_rating
                            nrv_lis[6] = rivals_offer_dict
                            nrv_lis[7] = height
                            nrv_lis[8] = weight
                            nrv_lis[9] = forty
                            nrv_lis[10] = shuttle
                            nrv_lis[11] = vertical
                            nrv_lis[12] = class_year
                            nrv_lis[13] = j_number
                            nrv_lis[14] = tweet
                            nrv_lis[15] = headshot_image
                            nrv_lis[16] = rivals_visit_dict
                    except Exception as e:
                        print(e)
                    try:
                        if len(a) == 3:
                            url = 'https://247sports.com/Season/{}-Football/Recruits/?&Player.FullName={}%20{}%20{}'.format(
                                classif, a[0].lower(), a[1].lower(),a[2].lower())
                        else:
                            url = 'https://247sports.com/Season/{}-Football/Recruits/?&Player.FullName={}%20{}'.format(
                                classif, a[0], a[1])
                        seven_driver_exception = ''
                        # retry_count = 2
                        # connection_reset_flag = ''
                        # for retries in range (retry_count):
                        #     try:
                        #         if connection_reset_flag == 'raised':
                        #             try:
                        #                 chrome_options = Options()
                        #                 chrome_options.add_argument("--headless")
                        #                 chrome_options.add_argument("--incognito")
                        #                 chrome_options.add_argument("disk-cache-size=0")
                        #                 chrome_options.add_argument("--disable-browser-cache-memory")
                        #                 chrome_options.add_argument("--disable-browser-cache-disk")
                        #                 chrome_options.add_argument("--disable-browser-cache-offline")
                        #                 chrome_options.add_argument("--disable-browser-cache-disk-enable")
                        #                 chrome_options.add_argument("--disable-cache-offline-enable")
                        #                 chrome_options.add_argument("--disable-network-http-use-cache")
                        #                 chrome_options.add_argument("--disable-dev-shm-usage")
                        #                 driver = webdriver.Chrome(options=chrome_options)
                        #             except Exception as e:
                        #                 print("{}".format(e))
                        try:
                            time.sleep(2)
                            driver.get(url)
                            #break
                        except UnboundLocalError as error:
                            seven_driver_exception = 'raised'
                        except Exception as e:
                                # if e.args[0] =='Connection aborted.':
                                #     connection_reset_flag = 'raised'
                                #     os.system("pgrep chrome | xargs kill -9")
                                #     continue
                                # elif e.args[0][0] == 'H':
                                #     connection_reset_flag = 'raised'
                                #     os.system("pgrep chrome | xargs kill -9")
                                #     continue
                                # elif 'chrome not reachable' in e.args[0]:
                                #     connection_reset_flag = 'raised'
                                #     continue
                                # else:
                            print(e)
                        if seven_driver_exception != 'raised':
                            try:
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                                    (By.XPATH, '/html/body/section/section/div/section[2]/section/section/section/div/div[1]/ul[2]/li/ul/li[2]/a')))
                                print("Page is ready!")
                            except TimeoutException:
                                print("Not in 247sports.com!")

                            html = driver.page_source
                            time.sleep(1)
                            soup = BeautifulSoup(html, 'html.parser')
                            name_link = soup.findAll('ul', {'class': 'player'})
                            flag = ''
                            if len(name_link) > 0:
                                player_profile = name_link[0].find('a').get('href')
                            results = soup.find('ul', {'class': 'results'})
                            if len(results.text) == 0:
                                driver.delete_all_cookies()
                                #driver.quit()
                                flag = 'Player Not found'
                                pass
                            elif 'No results found.' in results.text:
                                driver.delete_all_cookies()
                                #driver.quit()
                                flag = 'Player Not found'
                                pass
                            else:
                                profile_soup = None
                                profile_link = requests.get(player_profile, headers=HEADERS)
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
                                                else:
                                                    commit_date = ''    
                                                if commited_date.find('img'):
                                                    commit_school_logo = commited_date.find('img').get('data-src')
                                                    commit_school_logo = commit_school_logo.split('?')[0]
                                                else:
                                                    commit_school_logo = ''

                                        if commit_school_name != '' and commit_date != '' and commit_school_logo != '':
                                            seven_hard_commit = (commit_school_name,commit_date,commit_school_logo)
                                except Exception as e:
                                    print(e)
                                offers_seven = []
                                visits_seven = []
                                #driver.quit()
                                if state.lower().strip() in states_lis[-1].lower().strip() or city.lower().strip() in city_lis[-1].lower().strip() or school.lower().strip() in school_lis[-1].lower().strip():
                                    print(a[0]+" "+a[1], 'match')
                                    request_TL = None
                                    recruiting_profile_soup = None
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

                                    if recruiting_profile_soup != None:
                                        profile_soup = recruiting_profile_soup
                                        #requesting without Selenium
                                    if profile_soup.find('ul', {'class':'metrics-list'}):
                                        pos = profile_soup.find('ul', {'class':'metrics-list'})
                                        try:
                                            position = pos.find_all('span')[1].text
                                            ht = pos.find_all('span')[3].text
                                            height = ht.split('.')[0].replace('-','.')
                                            if height == '.':
                                                height = ''
                                            weight = pos.find_all('span')[5].text
                                            if weight == '-':
                                                weight = ''
                                        except Exception as e:
                                            print(e)
                                            print('exception in height ,weight of 247')
                                    else:
                                        height = ''
                                        weight = ''
                                        position = ''
                                    try:
                                        if profile_soup.find('div', {'class':'img-container'}):
                                            player_image = profile_soup.find('div', {'class':'img-container'})
                                            img_link = player_image.find('img').get('data-src')
                                            image_link = img_link.split('?')[0]
                                            if image_link == 'https://s3media.247sports.com/Uploads/Player/0/0.jpg':
                                                image_link = ''
                                        else:
                                            image_link = ''
                                    except Exception as e:
                                        print(e)        
                                    try:
                                        if profile_soup.find('div', {'class':'tweets-comp'}):
                                            twitter = profile_soup.find('div', {'class':'tweets-comp'})
                                            twitter_handle = twitter.get('data-username')

                                            if "@" in twitter_handle:
                                                tweet = twitter_handle
                                            else:
                                                tweet = '@'+twitter_handle
                                        else:
                                            tweet = ''
                                    except Exception as e:
                                        print(e)        

                                    try:    
                                        if profile_soup.find('h2',{'class':'composite-rank'}):
                                            star_rating = profile_soup.find('h2',{'class':'composite-rank'})
                                            rating = star_rating.text.replace('  i  ','').replace(' NA','').strip()
                                            star_ratingg = ''
                                            if rating != '':
                                                rating_obj = float(rating)
                                                if 0.0 <= rating_obj  <= 0.6999:
                                                    star_ratingg = 1
                                                elif 0.7000 <= rating_obj <= 0.7999:
                                                    star_ratingg = 2
                                                elif 0.8000 <= rating_obj <= 0.8900:
                                                    star_ratingg = 3
                                                elif 0.8901 <= rating_obj <= 0.9700:
                                                    star_ratingg = 4
                                                elif 0.9701 <= rating_obj <= 1:
                                                    star_ratingg = 5

                                        else:
                                            star_ratingg = ''
                                    except Exception as e:
                                        star_ratingg = ''
                                        #print(e)        
                                    if profile_soup.find('div' ,{"class":"body"}):
                                        forty_shuttle_verticle = profile_soup.find('div' ,{"class":"body"}).find_all('li')
                                        Forty = ''
                                        shuttle = ''
                                        vertical = ''
                                        try:
                                            if len(forty_shuttle_verticle) > 0:
                                                for fsv in forty_shuttle_verticle:
                                                    if fsv.find('span').text == 'Forty':
                                                        Forty = fsv.find('h3').text.strip()
                                                    elif fsv.find('span').text == 'Shuttle':
                                                        shuttle = fsv.find('h3').text.strip()
                                                    elif fsv.find('span').text == 'Vertical':
                                                        vertical = fsv.find('h3').text.strip()

                                        except Exception as e:
                                            print(e)
                                            print('exception occured in forty shuttle of 247')

                                    else:
                                        Forty = ''
                                        shuttle = ''
                                        vertical = ''
                                    # offers list
                                    try:
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
                                    except Exception as e:
                                        seven_offer_dict = {}
                                        seven_visit_dict = {}
                                else:
                                    state = ''
                                    city = ''
                                    school = ''
                                    position = ''
                                    height = ''
                                    weight = ''
                                    tweet = ''
                                    image_link = ''
                                    star_ratingg = ''
                                    Forty = ''
                                    shuttle = ''
                                    vertical = ''

                            if flag == 'Player Not found':
                                state = ''
                                city = ''
                                school = ''
                                position = ''
                                height = ''
                                weight = ''
                                tweet = ''
                                image_link = ''
                                star_ratingg = ''
                                Forty = ''
                                shuttle = ''
                                vertical = ''
                            #driver.quit()
                            jersey_number = ''
                            seven_lis[0] = a[0]+" "+a[1]
                            seven_lis[1] = state.strip()
                            seven_lis[2] = city
                            seven_lis[3] = school.strip()
                            seven_lis[4] = position
                            seven_lis[5] = star_ratingg
                            seven_lis[6] = seven_offer_dict
                            seven_lis[7] = height
                            seven_lis[8] = weight
                            seven_lis[9] = Forty.strip()
                            seven_lis[10] = shuttle.strip()
                            seven_lis[11] = vertical.strip()
                            seven_lis[12] = classif
                            seven_lis[13] = jersey_number
                            seven_lis[14] = tweet
                            seven_lis[15] = image_link
                            seven_lis[16] = seven_visit_dict

                    except Exception as e:
                        print(e)
                        driver.quit()
                        driver = get_driver()
                        time.sleep(5)
                        continue
                    try:
                        if seven_lis[4] != '':
                            player_position = seven_lis[4]
                        else:
                            if nrv_lis[4] != '':
                                player_position = nrv_lis[4]
                            else:
                                if max_lis[4] != '':
                                    player_position = max_lis[4]
                                else:
                                    player_position = None

                        if seven_lis[5] != '':
                            player_rating = float(seven_lis[5])
                        else:
                            if nrv_lis[5] != '':
                                player_rating = float(nrv_lis[5])
                            else:
                                player_rating = None

                        if seven_lis[6] != '':
                            player_offers = seven_lis[6]
                        else:
                            if nrv_lis[6] != '':
                                player_offers = nrv_lis[6]
                            else:
                                player_offers = None

                        if seven_lis[7] != '':
                            player_ht = seven_lis[7]
                        else:
                            if nrv_lis[7] != '':
                                player_ht = nrv_lis[7]
                            else:
                                if max_lis[7] != '':
                                    player_ht = max_lis[7]
                                else:
                                    player_ht = None
                    
                        if seven_lis[8] != '':
                            player_weight = float(seven_lis[8])
                        else:
                            if nrv_lis[8] != '':
                                player_weight = float(nrv_lis[8])
                            else:
                                if max_lis[8] != '':
                                    player_weight = float(max_lis[8])
                                else:
                                    player_weight = None

                        if seven_lis[9] != '':
                            player_forty_yard = float(seven_lis[9])
                        else:
                            player_forty_yard = None

                        if seven_lis[10] != '':
                            player_short_shuttle = float(seven_lis[10])
                        else:
                            player_short_shuttle = None

                        if seven_lis[11] != '':
                            player_vertical = float(seven_lis[11])
                        else:
                            player_vertical = None

                        if max_lis[13] != '':
                            player_jersey = max_lis[13]
                        else:
                            player_jersey = None

                        if seven_lis[14] != '':
                            player_twitter = seven_lis[14]
                        else:
                            player_twitter = None

                        if seven_lis[15] != '':
                            player_headshot_image = seven_lis[15]
                        else:
                            if nrv_lis[15] != '':
                                player_headshot_image = nrv_lis[15]
                            else:
                                if max_lis[15] != '':
                                    player_headshot_image = max_lis[15]
                                else:
                                    player_headshot_image = None

                        if seven_lis[16] != '':
                            player_visits = seven_lis[16]
                        else:
                            if nrv_lis[16] != '':
                                player_visits = nrv_lis[6]
                            else:
                                player_visits = None
                    except Exception as e:
                        print(e)
                    #comparison with database
                    try:
                        if player_twitter != None:
                            player.twitter_handle = player_twitter
                            if player.social_engagement != None:
                                player.social_engagement.twitter_handle = player_twitter
                            else:
                                try:
                                    social_obj = SocialEngagement.objects.get(twitter_handle=player_twitter)
                                    social_obj.save()
                                    player.social_engagement = social_obj
                                except SocialEngagement.DoesNotExist:
                                    social_obj = SocialEngagement.objects.create(twitter_handle=player_twitter)
                                    social_obj.save()
                                    player.social_engagement = social_obj

                        try:
                            if player_position != None:
                                position_list = player_position.split(',')
                                if len(position_list) > 0:
                                    for pos in position_list:
                                        try:
                                            pos_obj = Positions.objects.get(
                                                name__iexact=pos.strip())
                                            player.position.add(pos_obj)
                                        except Exception as e:
                                            pass
                        except Exception as e:
                            print(e)


                        if player_forty_yard != None:
                            player.fourty_yard_dash = player_forty_yard

                        if player_short_shuttle != None:
                            player.short_shuttle = player_short_shuttle

                        if player_vertical != None:
                            player.vertical = player_vertical

                        if player_jersey != None:
                            player.jersey_number = player_jersey

                        if player_rating != None:
                            player.star_rating = player_rating
                        if player_ht != None and player_ht != '':
                            if player_ht != None and player_ht != '':
                                player_ht = str(player_ht)
                                if len(player_ht) == 1:
                                    feet = int(player_ht)
                                    inches = 0
                                    player_height = (feet*12 + inches)
                                    player.height = player_height
                                else:
                                    if len(player_ht) >= 3:
                                        list_obj = player_ht.split('.')
                                        feet = int(list_obj[0])
                                    if len(list_obj) >= 2:
                                        inches = int(list_obj[1])
                                    else:
                                        inches = 0
                                    player_height = (feet*12 + inches)
                                    player.height = player_height
                        if player_weight != None and player_weight != '':
                            player.weight = player_weight


                        if player_headshot_image != None:
                            try:
                                if player_headshot_image:
                                    img_url = player_headshot_image
                                    ssl._create_default_https_context = ssl._create_unverified_context
                                    result = urllib2.urlretrieve(img_url)
                                    # image_name = img_url.split('/')[-1]
                                    player.profile_photo.save(
                                        os.path.basename(
                                            player.first_name + '-'
                                            + player.last_name + '.png'),
                                        File(open(result[0], 'rb'))
                                    )
                            except Exception as e:
                                print("{} Player Avatar not found in given URL {}".format(
                                    player.full_name, e))
                        else:
                            if player.profile_photo:
                                player.profile_photo = None              

                        player.save()
                    except Exception as e:
                        print(e)
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
                        else:
                            commit_school = None
                            commit_date = None
                        if len(rivals_decommit) > 0:
                            decommit_school = rivals_decommit[0]
                            decommit_date = rivals_decommit[1]
                    except Exception as e:
                        print(e)
                    try:
                        if len(fbs_schools) > 0:
                            fbs_schools = [sch.lower().strip() for sch in fbs_schools]
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