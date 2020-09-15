import requests
import re
from bs4 import BeautifulSoup
import csv
import os.path
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Player,Classification,OldPlayMakingValues


class Command(BaseCommand):
    """
        Use Case: python manage.py add_film_grades
    """
    help = 'Used to Importing FilmGrade Data from Athleticism score and \
        Playmaking score.'

    def handle(self, *args, **options):
        div_3 = 3*int(Player.objects.all().exclude(role__name__iexact='nfl').count()/4)
        div_4 = int(Player.objects.all().exclude(role__name__iexact='nfl').count())    
        player_playmaking= Player.objects.filter(priority__range=[div_3 + 1 ,div_4]).order_by('priority')
        for player in player_playmaking:
            try:
                school_lis = []
                try:
                    if player.school is not None:
                        school_lis.append(player.school.name)
                    else:
                        continue
                except Exception as e:
                    continue
                name = player.full_name
                a = name.split()
                try:
                    # https://www.maxpreps.com/search/default.aspx?type=athlete&search=Larry%20St.%20Pierre%20jr&state=&gendersport=boys,football
                    if len(a) == 3:
                        LINK_MAX = 'https://www.maxpreps.com/search/default.aspx?type=athlete&search={}%20{}%20{}&state=&gendersport=boys,football'.format(
                            a[0], a[1], a[2])
                    else:
                        LINK_MAX = 'https://www.maxpreps.com/search/default.aspx?type=athlete&search={}%20{}&state=&gendersport=boys,football'.format(
                            a[0], a[1])
                    time.sleep(3)
                    URL = requests.get(LINK_MAX)
                    rank_soup = BeautifulSoup(URL.content, 'html.parser')
                    link_max = ''
                    match_case = rank_soup.find_all('li', {'class': 'row result'})
                    for school_name in match_case:
                        #comp_lis[-1].replace(' High School','').strip() in school_name.find('div',{'class':'school-name row-column-2'}).text
                        if school_name.find('div', {'class': 'school-name row-column-2'}).find('a'):
                            result_school = school_name.find(
                                'div', {'class': 'school-name row-column-2'}).find('a').next
                            if result_school.lower().strip() in school_lis[-1].lower().strip():
                                link_max = school_name.find(
                                    'div', {'class': 'athlete-name row-column-1'}).find('a', href=True).get('href')
                                break

                    if link_max == '':
                        #print(a, 'seraching in videos')
                        if len(a) == 3:
                            video_page = 'https://www.maxpreps.com/search/default.aspx?type=video&search={}%20{}%20{}&state=&gendersport=boys,football'.format(
                                a[0], a[1], a[2])
                        else:
                            video_page = 'https://www.maxpreps.com/search/default.aspx?type=video&search={}%20{}&state=&gendersport=boys,football'.format(
                                a[0], a[1])
                        video_page_link = requests.get(video_page)
                        video_soup = BeautifulSoup(video_page_link.content, 'html.parser')
                        schools = video_soup.find('ul', {'class': 'videos-list'})
                        if schools:
                            list_of_schools = schools.find_all('li')
                            for school_match in list_of_schools:
                                if school_match.find('span', {'style': 'color: #3778b4'}):
                                    school_matching = school_match.find(
                                        'span', {'style': 'color: #3778b4'}).text
                                    if school_lis[-1].strip() in school_matching:
                                        link_max = school_match.find('a').get('href')
                                        break

                    if link_max != '':
                        rq_profile = requests.get(link_max)
                        profile_soup = BeautifulSoup(rq_profile.content, 'html.parser')
                        if profile_soup.findAll('div', {'class': 'athlete-attributes'}):
                            points = profile_soup.findAll(
                                'div', {'class': 'athlete-attributes'})

                            if points[0].find('span', {'class': 'graduation-year'}):
                                pl_class = points[0].find(
                                    'span', {'class': 'graduation-year'}).text.replace('Graduates in ', '')
                                if 'Graduated in ' in pl_class:
                                    pl_class = pl_class.replace('Graduated in ', '')

                            else:
                                pl_class = ''
                        else:
                            pl_class = ''
                        if player.classification is not None and  player.classification.year is not None:
                            if pl_class.strip() == player.classification.year.strip():
                                # if profile_soup.find('li',{'class':'active'}):
                                if profile_soup.find_all('ul', {'class': 'career-navigation nav nav-pills'}):
                                    lk = profile_soup.find_all(
                                        'ul', {'class': 'career-navigation nav nav-pills'})
                                    football_links = lk[0].find_all('li')
                                    for carrer_stats in football_links:
                                        Intc = ''
                                        Sacks = ''
                                        touchd = ''
                                        if carrer_stats.text == 'Football' or carrer_stats.text == 'FB':
                                            fb = carrer_stats.find('a').get('href')
                                            stats_page = 'https://www.maxpreps.com'+fb
                                            playmaking_URL = requests.get(stats_page)
                                            playmaking_soup = BeautifulSoup(
                                                playmaking_URL.content, 'html.parser')
                
                                            if playmaking_soup.find('div', {'class': 'stats-grids'}):
                                                if playmaking_soup.find('div', {'class': 'stats-grids'}).find_all('div'):
                                                    categories = playmaking_soup.find(
                                                        'div', {'class': 'stats-grids'}).find_all('div')
                                                    for category_check in categories:
                                                        catg = category_check.find('h4').text
                                                        if 'Sacks' in catg:
                                                            #category_check.find('table',{'class':'mx-grid sortable stats-grid'})
                                                            if category_check.find('tr', {'class': 'first last'}):
                                                                catg_check = category_check.find(
                                                                    'tr', {'class': 'first last'})
                                                                if catg_check.find('td', {'class': 'year first'}):
                                                                    year = catg_check.find(
                                                                        'td', {'class': 'year first'}).text
                                                                    if '19-20' in year:
                                                                        if category_check.find('tr', {'class': 'first last'}).find('td', {'class': 'sacks stat dw'}):
                                                                            Sacks = category_check.find('tr', {'class': 'first last totals'}).find(
                                                                                'td', {'class': 'sacks stat dw'}).text
                                                            if Sacks == '':
                                                                if category_check.find('tr', {'class': 'first'}):
                                                                    catg_check = category_check.find(
                                                                        'tr', {'class': 'first'})
                                                                    if catg_check.find('td', {'class': 'sacks stat dw'}):
                                                                        Sacks = catg_check.find(
                                                                            'td', {'class': 'sacks stat dw'}).text


                                                        if 'Touchdowns' in catg:
                                                            if category_check.find('tbody'):
                                                                if category_check.find('tbody').find_all('tr'):
                                                                    year_check = category_check.find(
                                                                        'tbody').find_all('tr')
                                                                    for junior in year_check:
                                                                        if junior.find('td', {'class': 'year first'}):
                                                                            jnior_year = junior.find(
                                                                                'td', {'class': 'year first'}).text
                                                                            if '19-20' in jnior_year:
                                                                                if junior.find('td', {'class': 'totaltdnum stat dw'}):
                                                                                    touchd = junior.find(
                                                                                        'td', {'class': 'totaltdnum stat dw'}).text

                                                                    #touchd = category_check.find('tr',{'class':'first last totals'}).find('td',{'class':'totaltdnum stat dw'}).text
                                                        if 'Defensive Statistics' in catg:
                                                            if category_check.find('tbody'):
                                                                if category_check.find('tbody').find_all('tr'):
                                                                    year_check = category_check.find(
                                                                        'tbody').find_all('tr')
                                                                    for junior in year_check:
                                                                        if junior.find('td', {'class': 'year first'}):
                                                                            jnior_year = junior.find(
                                                                                'td', {'class': 'year first'}).text
                                                                            if '19-20' in jnior_year:
                                                                                if junior.find('td', {'class': 'ints stat dw'}):
                                                                                    Intc = junior.find(
                                                                                        'td', {'class': 'ints stat dw'}).text

                                            #if pl_class == '2020':
                                            if Intc != (None or ''):
                                                Intc = float(Intc)
                                            else:
                                                Intc = None

                                            if Sacks != (None or ''):
                                                Sacks = float(Sacks)
                                            else:
                                                Sacks = None
                                            if touchd != (None or ''):
                                                touchd = float(touchd)
                                            else:
                                                touchd = None
                                            
                                            playmaking_obj = OldPlayMakingValues.objects.filter(player=player.id)
                                            if playmaking_obj:
                                                playmaking_obj = playmaking_obj[0]
                                                if playmaking_obj.old_interception_maxpreps == None and Intc != (None or '') :
                                                    playmaking_obj.old_interception_maxpreps = Intc
                                                    player.interception = Intc
                                                
                                                elif playmaking_obj.old_interception_maxpreps != None and Intc != (None or ''):
                                                    if playmaking_obj.old_interception_maxpreps != Intc:
                                                        playmaking_obj.old_interception_maxpreps = Intc
                                                        player.interception = Intc
                                                if playmaking_obj.old_sack_maxpreps == None and Sacks != (None or ''):
                                                    playmaking_obj.old_sack_maxpreps = Sacks
                                                    player.sack = Sacks

                                                elif playmaking_obj.old_sack_maxpreps != None and Sacks != (None or ''):
                                                    if playmaking_obj.old_sack_maxpreps != Sacks:
                                                        playmaking_obj.old_sack_maxpreps = Sacks
                                                        player.sack = Sacks

                                                if playmaking_obj.old_touchdown_maxpreps == None and touchd != (None or '') :
                                                    playmaking_obj.old_touchdown_maxpreps = touchd
                                                    player.touchdown = touchd
                                                elif playmaking_obj.old_touchdown_maxpreps != None and touchd != (None or ''):
                                                    if playmaking_obj.old_touchdown_maxpreps != touchd:
                                                        playmaking_obj.old_touchdown_maxpreps = touchd
                                                        player.touchdown =touchd 
                                            else:
                                                print(player.full_name,"not in OldPlayMakingValues table")
                                            player.save()
                                            print(player.full_name , player.interception ,player.sack, player.touchdown)

                except Exception as e:
                    print(e)
                    print(a)
            except Exception as e:
                print(e)