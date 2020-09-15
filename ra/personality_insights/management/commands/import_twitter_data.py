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

    help = 'Used to add Personality Insights for Players'

    def handle(self, *args, **options):
        # The Twitter API credentials
        twitter_consumer_key = config.get('twitter_consumer_key')
        twitter_consumer_secret = config.get('twitter_consumer_secret')
        twitter_access_token = config.get('twitter_access_token')
        twitter_access_secret = config.get('twitter_access_secret')

        # Invoking the Twitter API
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        twitter_api = twitter.Api(consumer_key=twitter_consumer_key,
                                  consumer_secret=twitter_consumer_secret,
                                  access_token_key=twitter_access_token,
                                  access_token_secret=twitter_access_secret
                                  )

        twitter_handle_players = Player.objects.filter(
            twitter_handle__isnull=False).distinct()
        print(len(twitter_handle_players), '-players num of handles')

        for player in twitter_handle_players:
            try:
                handle = player.twitter_handle
                if handle != '':
                    # Retrieving the last no of tweets from a user
                    ssl._create_default_https_context = ssl._create_unverified_context
                    statuses = twitter_api.GetUserTimeline(
                        screen_name=unidecode(handle), count=200, include_rts=False)
                    tweets_followers_counts = twitter_api.GetUser(
                        screen_name=unidecode(handle))
                    no_of_followers = tweets_followers_counts.followers_count
                    no_of_followings = tweets_followers_counts.friends_count
                    no_of_tweets = tweets_followers_counts.statuses_count
                    try:
                        twitter_social = SocialEngagement.objects.get(
                            twitter_handle=handle,
                        )
                        if no_of_followers:
                            twitter_social.followers = str(no_of_followers)
                        if no_of_followings:
                            twitter_social.following = str(no_of_followings)
                        if no_of_tweets:
                            twitter_social.tweets = str(no_of_tweets)
                        if tweets_followers_counts.status != None:
                            recent_tweet = tweets_followers_counts.status.text
                            twitter_social.last_tweet = recent_tweet
                        twitter_social.save()

                    except SocialEngagement.DoesNotExist:
                        twitter_social = SocialEngagement.objects.create(
                            twitter_handle=handle,
                        )
                        if no_of_followers:
                            followers = str(no_of_followers)
                            twitter_social.followers = followers
                        if no_of_followings:
                            following = str(no_of_followings)
                            twitter_social.following = following
                        if no_of_tweets:
                            tweets = str(no_of_tweets)
                            twitter_social.tweets = tweets
                        twitter_social.save()
                        if tweets_followers_counts.status != None:
                            recent_tweet = tweets_followers_counts.status.text
                            twitter_social.last_tweet = recent_tweet
                        twitter_social.save()

                    player.social_engagement = twitter_social
                    player.last_twitter_status = recent_tweet
                    player.save()
                    print(player.full_name, " :- twitter data has been updated successfully")

            except Exception as e:
                print(player.full_name, e)
        print("All players twitter data added successfully")
