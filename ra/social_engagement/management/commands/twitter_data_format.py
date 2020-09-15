import csv
import json
import os
import sys
import ssl
import re
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

    help = 'Used to Formatted twitter data points'

    def handle(self, *args, **options):
        all_twitter = SocialEngagement.objects.filter(
            followers__isnull=False,
            following__isnull=False,
            tweets__isnull=False
        )
        for twit in all_twitter:
            followers = re.sub(r"[^0-9]", "", twit.followers)
            following = re.sub(r"[^0-9]", "", twit.following)
            tweets = re.sub(r"[^0-9]", "", twit.tweets)
            twit.followers = followers
            twit.following = following
            twit.tweets = tweets
            twit.save()
