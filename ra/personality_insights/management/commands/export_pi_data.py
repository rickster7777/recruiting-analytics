import csv
import json
import os
import sys
import ssl
import requests
import twitter
import urllib3
from django.core.management.base import BaseCommand
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import PersonalityInsightsV3
from unidecode import unidecode
from players.models import Player
from social_engagement.models import SocialEngagement
from personality_insights.models import (PersonalityInsights, ProspectsNeeds,
                                         ProspectsPersonality, ProspectsValues)
from ra.settings.config_ra import main_conf as config


class Command(BaseCommand):

    help = 'Used to Export Personality Insights for Players'

    def handle(self, *args, **options):
        all_players = Player.objects.filter(twitter_handle__isnull=False)
        for player in all_players:
            if player.twitter_handle != '':
                if player.personality_insight:
                    data = []
                    # personality
                    data.append(player.full_name)
                    data.append(player.twitter_handle)
                    print('success to get')
                    coachability = player.personality_insight.personality.coachability
                    data.append(coachability)
                    teamplayer = player.personality_insight.personality.team_player
                    data.append(teamplayer)
                    extroverted = player.personality_insight.personality.extroverted
                    data.append(extroverted)
                    temperament = player.personality_insight.personality.temperament
                    data.append(temperament)
                    openness = player.personality_insight.personality.openness
                    data.append(openness)
                    # personality_obj = pi_obj.personality

                    # needs
                    challenge = player.personality_insight.needs.challenge
                    data.append(challenge)
                    excitement = player.personality_insight.needs.excitement
                    data.append(excitement)
                    ideal = player.personality_insight.needs.ideal
                    data.append(ideal)
                    stability = player.personality_insight.needs.stability
                    data.append(stability)
                    structure = player.personality_insight.needs.structure
                    data.append(structure)

                    # values
                    achievement = player.personality_insight.values.achievement
                    data.append(achievement)
                    helping_others = player.personality_insight.values.helping_others
                    data.append(helping_others)
                    stimulation = player.personality_insight.values.stimulation
                    data.append(stimulation)
                    taking_pleasure_in_life = player.personality_insight.values.taking_pleasure_in_life
                    data.append(taking_pleasure_in_life)
                    tradition = player.personality_insight.values.tradition
                    data.append(tradition)

                    with open("/home/kapil/Desktop/ra_repo/ra/ra/personality_insights/management/commands/exported_csv.csv", 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(data)
                        print(player.first_name,
                              'player PI data exported successfully')
                        data = []
