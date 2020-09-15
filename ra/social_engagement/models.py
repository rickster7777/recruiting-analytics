from django.db import models

# Create your models here.


class SocialEngagement(models.Model):
    twitter_handle = models.CharField(max_length=250, null=True, blank=True)
    followers = models.CharField(max_length=16, null=True, blank=True)
    following = models.CharField(max_length=16, null=True, blank=True)
    new_followers = models.CharField(max_length=16, null=True, blank=True)
    key_people_followers = models.CharField(
        max_length=16, null=True, blank=True)
    key_people_followings = models.CharField(
        max_length=16, null=True, blank=True)
    tweets = models.CharField(max_length=16, null=True, blank=True)
    retweets = models.CharField(max_length=16, null=True, blank=True)
    newly_followed = models.CharField(max_length=16, null=True, blank=True)
    last_tweet = models.TextField(null=True, blank=True)
