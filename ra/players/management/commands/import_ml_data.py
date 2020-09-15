import ast
import csv
import io
import json
import os.path
import re
import os
import ssl
import time
import urllib.request as urllib2
from json.decoder import JSONDecodeError
from json.decoder import JSONDecodeError
import requests
import xlrd
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Q
from requests.auth import HTTPBasicAuth

from players.models import Player,OldPlayMakingValues
from ra.settings.config_ra import main_conf as config
import glob


ml_api_auth = HTTPBasicAuth(config.get('API_USER'), config.get('API_PASSWORD'))


class Command(BaseCommand):
    """
        Use Case: python manage.py import_ml_data

    """
    help = 'Used for updating athleticism score from ML API'

    def handle(self, *args, **options):
        url = config.get('ATHLETICISM_API')

        all_players = Player.objects.all().order_by('priority')
        for player_obj in all_players:
            try:
                player_id = str(player_obj.id)
                data_json = url + player_id + '/'
                try:
                    data = requests.get(data_json, auth=ml_api_auth)
                    player_data = data._content
                    decoded_data = player_data.decode("utf-8")
                    if decoded_data != None:
                        json_data = json.loads(decoded_data)
                    else:
                        json_data = None
                except JSONDecodeError:
                    print('JSONDecodeError occurred')
                    json_data = None
                except Exception as e:
                    json_data = None
                # json_data = ast.literal_eval(decoded_data)
                if json_data != None:
                    if not 'Result' in json_data.keys():
                        try:
                            athleticism_obj = OldPlayMakingValues.objects.filter(player=player_id)
                            if athleticism_obj:
                                athleticism_obj = athleticism_obj[0]
                            player_uuid = json_data['id']
                            player = Player.objects.get(id=player_uuid)
                            topspeed = json_data['TopSpeed']['value']
                            if topspeed:
                                top_speed_val = float("%.2f" % round(topspeed, 2))
                                if athleticism_obj:                                    
                                    if athleticism_obj.old_top_speed == None and top_speed_val != (None or ''):
                                        athleticism_obj.old_top_speed = top_speed_val
                                        player.top_speed = top_speed_val 
                                    elif athleticism_obj.old_top_speed != None and top_speed_val != (None or ''):
                                        if athleticism_obj.old_top_speed != top_speed_val:
                                            athleticism_obj.old_top_speed = top_speed_val
                                            player.top_speed = top_speed_val
                            topspeedrank = json_data['TopSpeedRank']
                            if topspeedrank:
                                topspeedrank = int(json_data['TopSpeedRank'])
                                if player.top_speed_rank is None:
                                    player.top_speed_rank = topspeedrank
                            time_to_top_speed = json_data['TimetoTopSpeed']['value']
                            if time_to_top_speed:
                                timetotopspeed = float(
                                    "%.2f" % round(time_to_top_speed, 2))
                                if athleticism_obj:
                                    if athleticism_obj.old_time_to_top_speed == None and timetotopspeed != (None or ''):
                                        athleticism_obj.old_time_to_top_speed = timetotopspeed
                                        player.time_to_top_speed = timetotopspeed 
                                    elif athleticism_obj.old_time_to_top_speed != None and timetotopspeed != (None or ''):
                                        if athleticism_obj.old_time_to_top_speed != timetotopspeed:
                                            athleticism_obj.old_time_to_top_speed = timetotopspeed
                                            player.time_to_top_speed = timetotopspeed   
                            time_to_top_speed_rank = json_data['TimetoTopSpeedRank']
                            if time_to_top_speed_rank:
                                time_to_top_speed_rank_val = int(
                                    time_to_top_speed_rank)
                                if player.time_to_top_speed_rank is None:
                                    player.time_to_top_speed_rank = \
                                        time_to_top_speed_rank_val
                            avg_yards_of_seperation = \
                                json_data['AvgYardsofSeperation']['value']
                            if avg_yards_of_seperation:
                                avg_yards_of_seperation_val = float(
                                    "%.2f" % round(avg_yards_of_seperation, 2))
                                if athleticism_obj:
                                    if athleticism_obj.old_avg_yards_of_seperation == None and avg_yards_of_seperation_val != (None or ''):
                                        athleticism_obj.old_avg_yards_of_seperation = avg_yards_of_seperation_val
                                        player.avg_yards_of_seperation = avg_yards_of_seperation_val 
                                    elif athleticism_obj.old_avg_yards_of_seperation != None and avg_yards_of_seperation_val != (None or ''):
                                        if athleticism_obj.old_avg_yards_of_seperation != avg_yards_of_seperation_val:
                                            athleticism_obj.old_avg_yards_of_seperation = avg_yards_of_seperation_val
                                            player.avg_yards_of_seperation = avg_yards_of_seperation_val
                            avg_yards_of_seperation_rank = \
                                json_data['AvgYardsofSeperationRank']
                            if avg_yards_of_seperation_rank:
                                avg_yards_of_seperation_rank_val = int(
                                    avg_yards_of_seperation_rank)
                                if player.avg_yards_of_seperation_rank is None:
                                    player.avg_yards_of_seperation_rank = \
                                        avg_yards_of_seperation_rank_val
                            avg_closing_speed = \
                                json_data['AvgClosingSpeed']['value']
                            if avg_closing_speed:
                                avg_closing_speed_val = float(
                                    "%.2f" % round(avg_closing_speed, 2))
                                if athleticism_obj:
                                    if athleticism_obj.old_avg_closing_speed == None and avg_closing_speed_val != (None or ''):
                                        athleticism_obj.old_avg_closing_speed = avg_closing_speed_val
                                        player.avg_closing_speed = avg_closing_speed_val 
                                    elif athleticism_obj.old_avg_closing_speed != None and avg_closing_speed_val != (None or ''):
                                        if athleticism_obj.old_avg_closing_speed != avg_closing_speed_val:
                                            athleticism_obj.old_avg_closing_speed = avg_closing_speed_val
                                            player.avg_closing_speed = avg_closing_speed_val
                                
                            avg_closing_speed_rank = \
                                json_data['AvgClosingSpeedRank']
                            if avg_closing_speed_rank:
                                avg_closing_speed_rank_val = int(
                                    avg_closing_speed_rank)
                                if player.avg_closing_speed_rank is None:
                                    player.avg_closing_speed_rank = \
                                        avg_closing_speed_rank_val
                            avg_transition_time = json_data['AvgTransitionTime']['value']
                            if avg_transition_time:
                                avg_transition_time_val = float(
                                    "%.2f" % round(avg_transition_time, 2))
                                if athleticism_obj:
                                    if athleticism_obj.old_avg_transition_time == None and avg_transition_time_val != (None or ''):
                                        athleticism_obj.old_avg_transition_time = avg_transition_time_val
                                        player.avg_transition_time = avg_transition_time_val 
                                    elif athleticism_obj.old_avg_transition_time != None and avg_transition_time_val != (None or ''):
                                        if athleticism_obj.old_avg_transition_time != avg_transition_time_val:
                                            athleticism_obj.old_avg_transition_time = avg_transition_time_val
                                            player.avg_transition_time = avg_transition_time_val
                            avg_transition_time_rank = json_data['AvgTransitionTimeRank']
                            if avg_transition_time_rank:
                                avg_transition_time_rank_val = int(
                                    avg_transition_time_rank)
                                if player.avg_transition_time_rank is None:
                                    player.avg_transition_time_rank = \
                                        avg_transition_time_rank_val
                            #TODO Athleticism, we have separate job for calculating scores for athleticism
                            # athleticism_score = json_data['AthleticismScore']
                            # if athleticism_score:
                            #     athleticism_score_val = float(
                            #         "%.2f" % round(athleticism_score, 2))
                            #     player.athleticism = athleticism_score_val
                            total_athleticism_score_value = \
                                json_data['total_athleticism_score_value']
                            if total_athleticism_score_value:
                                total_athleticism_score_val = float(
                                    "%.2f" % round(total_athleticism_score_value, 2))
                                if player.total_athleticism_score_value is None:
                                    player.total_athleticism_score_value = \
                                        total_athleticism_score_val
                            athleticism_score_rank = json_data['AthleticismScoreRank']
                            if athleticism_score_rank:
                                athleticism_score_rank_val = int(
                                    athleticism_score_rank)
                                if player.athleticism_score_rank is None:
                                    player.athleticism_score_rank = \
                                        athleticism_score_rank_val
                            highlighted_video = json_data['video_links']
                            player.save()
                            try:
                                if highlighted_video:
                                    if player.video_highlight is None:
                                        player.video_highlight = highlighted_video
                                        player.save()
                                    video_url = highlighted_video
                                    try:
                                        ssl._create_default_https_context = ssl._create_unverified_context
                                        result = urllib2.urlretrieve(video_url)
                                        player.web_highlighted_video.save(
                                        os.path.basename(player.first_name + player.last_name + '-highlighted-video.mp4'),
                                        File(open(result[0], 'rb'))
                                        )
                                        player.save()
                                    except Exception as e:
                                        print(e, "video url error")

                                    tmp_files = glob.glob('/tmp/tmp*')
                                    remove_temps = [os.remove(file) for file in tmp_files]
                                    goog_files = glob.glob('/tmp/.com.google.Chr*')
                                    remove_good_tmps = [os.remove(file) for file in goog_files]
                                    driv_files = glob.glob('/tmp/*.dmp')
                                    remove_driv_tmp_files = [os.remove(file) for file in driv_files]
                            except Exception as e:
                                print(e)
                            player.save()
                            print(player.full_name, ' has been analyzed successfully')
                        except KeyError:
                            print("Result not Found")
            except Player.DoesNotExist:
                print("'{}' player UUID till not analyzed".format(
                    player_obj.full_name))
            except Exception as e:
                print(player_obj.full_name, ' - ' , e)
