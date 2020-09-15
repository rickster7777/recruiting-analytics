from django.db.models import Q
import sys
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from rest_framework import serializers
import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from address.models import City, School, State
from django.contrib.postgres.fields import JSONField
User = get_user_model()


class Team(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True,
                            )
    logo = models.FileField(
        upload_to='Teams/', blank=True, null=True)


class Classification(models.Model):
    year = models.CharField(max_length=150, null=True, blank=True,
                            unique=True)

    def __str__(self):
        return str(self.year) if self.year else ''


class PlayerType(models.Model):
    name = models.CharField(max_length=150, null=True,
                            blank=False, unique=False)

    def __str__(self):
        return str(self.name) if self.name else ''


class PositionGroup(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    detailed_name = models.CharField(max_length=50, null=True, blank=True)
    STATUS_CHOICES = (
        ("active", "active"),
        ("inactive", "inactive"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='inactive'
    )

    def __str__(self):
        return str(self.name) if self.name else ''


class Positions(models.Model):
    name = name = models.CharField(max_length=150, null=True, blank=True,
                                   unique=True)
    group = models.ForeignKey(PositionGroup,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL
                              )
    groups = models.ManyToManyField(
        PositionGroup, blank=True,
        related_name='position_groups'
    )

    def __str__(self):
        return str(self.name) if self.name else ''


class Notes(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    comments = models.ManyToManyField('players.Comments', blank=True,
                                      related_name='note_comments'
                                      )
    created_by = models.ForeignKey('ra_user.User',
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL
                                   )
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Overriding the save method to save updated_on data automatically
        Need to override updated_on from API.
        """

        if self.pk:
            self.updated_on = timezone.now()
        super(Notes, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title) if self.title else ''


class SchoolsVisit(models.Model):
    total = models.CharField(max_length=5, null=True, blank=True)
    schools = models.ManyToManyField(School, blank=True,
                                     related_name='schools_visit'
                                     )


class FbsHardCommit(models.Model):
    commited_on = models.CharField(blank=True, null=True, max_length=150)
    school = models.ForeignKey(School,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL
                               )


class FbsDeCommit(models.Model):
    decommited_on = models.CharField(blank=True, null=True, max_length=150)
    school = models.ForeignKey(School,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL
                               )


class FbsOffers(models.Model):
    total = models.CharField(max_length=5, null=True, blank=True)
    # schools = models.ManyToManyField(School, blank=True, null=True,
    #                                  related_name='fbs_offers'

    #                                  )
    hard_commit = models.ForeignKey(FbsHardCommit,
                                    blank=True, null=True,
                                    on_delete=models.SET_NULL
                                    )
    decommit = models.ForeignKey(FbsDeCommit,
                                 blank=True, null=True,
                                 on_delete=models.SET_NULL
                                 )
    visits = models.ForeignKey(SchoolsVisit,
                               blank=True, null=True,
                               on_delete=models.SET_NULL
                               )
    schools = models.ManyToManyField(
        School,
        related_name='new_schools',
        blank=True,
        through='FbsSchools'
    )


class FbsSchools(models.Model):
    fbs_offer = models.ForeignKey(
        FbsOffers,
        on_delete=models.CASCADE
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE
    )
    added_on = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = (
        ("old", "old"),
        ("new", "new"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='old'
    )

    class Meta:
        ordering = ('-added_on',)


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    full_name = models.CharField(max_length=250, null=True, blank=True)
    profile_photo = models.FileField(
        upload_to='Players/', blank=True, null=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    fourty_yard_dash = models.FloatField(null=True, blank=True)
    short_shuttle = models.FloatField(null=True, blank=True)
    vertical = models.FloatField(null=True, blank=True)
    hundred_yard_dash = models.FloatField(null=True, blank=True)
    twitter_handle = models.CharField(null=True, blank=True, max_length=250)
    jersey_number = models.IntegerField(null=True, blank=True)
    role = models.ForeignKey(PlayerType,
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL
                             )
    position = models.ManyToManyField(Positions, blank=True,
                                      related_name='player_positions')
    school = models.ForeignKey(School,
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL
                               )
    classification = models.ForeignKey(
        Classification,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    city = models.ForeignKey(City,
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL
                             )
    state = models.ForeignKey(State,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL
                              )
    star_rating = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    film_grade = models.FloatField(null=True, blank=True)
    athleticism = models.FloatField(null=True, blank=True)
    total_athleticism_score_value = models.FloatField(null=True, blank=True)
    athleticism_score_rank = models.IntegerField(null=True, blank=True)
    play_making = models.FloatField(null=True, blank=True)
    play_making_raw_score = models.FloatField(null=True, blank=True)
    gpa = models.FloatField(null=True, blank=True)
    sat = models.FloatField(null=True, blank=True)
    act = models.FloatField(null=True, blank=True)
    avg_transition_time = models.FloatField(null=True, blank=True)
    avg_transition_time_rank = models.IntegerField(null=True, blank=True)
    avg_completion_time = models.FloatField(null=True, blank=True)
    avg_yards_of_seperation = models.FloatField(null=True, blank=True)
    avg_yards_of_seperation_rank = models.IntegerField(null=True, blank=True)
    top_speed = models.FloatField(null=True, blank=True)
    top_speed_rank = models.IntegerField(null=True, blank=True)
    time_to_top_speed = models.FloatField(null=True, blank=True)
    time_to_top_speed_rank = models.IntegerField(null=True, blank=True)
    explosive_plays_allowed = models.FloatField(null=True, blank=True)
    avg_closing_speed = models.FloatField(null=True, blank=True)
    avg_closing_speed_rank = models.IntegerField(null=True, blank=True)
    catch_rate = models.FloatField(null=True, blank=True)
    qb_passer_rating = models.FloatField(null=True, blank=True)
    avg_yards_after_catch_allowed = models.FloatField(null=True, blank=True)
    personality_insight = models.ForeignKey(
        'personality_insights.PersonalityInsights',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    fbs_offers = models.ForeignKey(FbsOffers,
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL
                                   )
    notes = models.ManyToManyField(Notes, blank=True,
                                   related_name='player_notes')
    priority = models.IntegerField(null=True, blank=True)
    nfl_logo = models.FileField(
        upload_to='Players/', blank=True, null=True)
    video_highlight = models.URLField(max_length=650, null=True, blank=True,)
    social_engagement = models.ForeignKey(
        'social_engagement.SocialEngagement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(blank=True, null=True)
    last_twitter_status = models.TextField(null=True, blank=True)
    team = models.ForeignKey(Team,
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL
                             )
    sack = models.FloatField(null=True, blank=True)
    interception = models.FloatField(null=True, blank=True)
    touchdown = models.FloatField(null=True, blank=True)
    video_highlight_duration = models.CharField(
        max_length=50, null=True, blank=True
    )
    web_highlighted_video = models.FileField(
        upload_to='player-highlighted-video/', blank=True, null=True)

    def __str__(self):
        return str(self.first_name) if self.first_name else ''


@receiver(post_save, sender=Player)
def update_uc_player(sender, instance, created, **kwargs):

    if created:
        uc_role = PlayerType.objects.get(name__iexact='undercruited')
        prospect_role = PlayerType.objects.get(name__iexact='prospect')

        nfl_players = Player.objects.filter(
            role__name__iexact='nfl', film_grade__isnull=False).distinct()

        for nfl in list(nfl_players):
            nfl_filmgrade = nfl.film_grade
            nfl_height = nfl.height
            nfl_weight = nfl.weight
            nfl_positions = nfl.position.all()
            filters = {}
            filters['film_grade__isnull'] = False
            filters['height__isnull'] = False
            filters['weight__isnull'] = False
            filters['id'] = str(instance.id)
            uc_matched_player = Player.objects.filter(
                Q(
                    Q(**filters) &
                    Q(role__name__in=['prospect', 'undercruited']) &
                    Q(film_grade__lte=nfl_filmgrade + 3.0) &
                    Q(film_grade__gte=nfl_filmgrade - 3.0)
                ) &
                Q(
                    (
                        Q(height__lte=nfl_height + 1) &
                        Q(height__gte=nfl_height - 1)
                    ) &
                    (
                        Q(weight__lte=nfl_weight + 15.0) &
                        Q(weight__gte=nfl_weight - 15.0)
                    )
                )
            ).distinct()
            if len(uc_matched_player) > 0:
                if instance.role != None and 'nfl' != instance.role.name:
                    Player.objects.filter(id=instance.id).update(role=uc_role)
                    break
            else:
                if instance.role != None and 'nfl' != instance.role.name:
                    Player.objects.filter(id=instance.id).update(
                        role=prospect_role)
    else:
        uc_role = PlayerType.objects.get(name__iexact='undercruited')
        prospect_role = PlayerType.objects.get(name__iexact='prospect')

        nfl_players = Player.objects.filter(
            role__name__iexact='nfl', film_grade__isnull=False).distinct()

        for nfl in list(nfl_players):
            nfl_filmgrade = nfl.film_grade
            nfl_height = nfl.height
            nfl_weight = nfl.weight
            nfl_positions = nfl.position.all()
            filters = {}
            filters['film_grade__isnull'] = False
            filters['height__isnull'] = False
            filters['weight__isnull'] = False
            filters['id'] = str(instance.id)
            uc_matched_player = Player.objects.only(
                'id', 'role', 'film_grade', 'height', 'weight',
                'classification', 'position').filter(
                Q(
                    Q(**filters) &
                    Q(role__name__in=['prospect', 'undercruited']) &
                    Q(film_grade__lte=nfl_filmgrade + 3.0) &
                    Q(film_grade__gte=nfl_filmgrade - 3.0)
                ) &
                Q(
                    (
                        Q(height__lte=nfl_height + 1) &
                        Q(height__gte=nfl_height - 1)
                    ) &
                    (
                        Q(weight__lte=nfl_weight + 15.0) &
                        Q(weight__gte=nfl_weight - 15.0)
                    )
                )
            ).distinct()
            if len(uc_matched_player) > 0:
                if instance.role != None and 'nfl' != instance.role.name:
                    Player.objects.filter(id=instance.id).update(role=uc_role)
                break
            else:
                if instance.role != None and 'nfl' != instance.role.name:
                    Player.objects.filter(id=instance.id).update(
                        role=prospect_role)


class SavedSearch(models.Model):
    name = models.CharField(max_length=150, null=False,
                            blank=False,)
    search_by = models.ForeignKey('ra_user.User',
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL
                                  )
    fitfinder_search = JSONField(null=True)
    searched_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('name', 'search_by',)
        ordering = ('-searched_on', )


class Comments(models.Model):
    message = models.TextField(null=False, blank=False)
    commented_by = models.ForeignKey('ra_user.User',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL
                                     )
    updated_on = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """
        Overriding the save method to save updated_on data automatically
        Need to override updated_on from API.
        """

        if self.pk:
            self.updated_on = timezone.now()
        super(Comments, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.message) if self.message else ''


class OldPlayMakingValues(models.Model):
    old_sack_maxpreps = models.FloatField(null=True, blank=True)
    old_interception_maxpreps = models.FloatField(null=True, blank=True)
    old_touchdown_maxpreps = models.FloatField(null=True, blank=True)
    player = models.ForeignKey(
            'players.Player',
            on_delete=models.CASCADE
        )
    old_avg_transition_time  = models.FloatField(null=True, blank=True)
    old_avg_closing_speed =  models.FloatField(null=True, blank=True)
    old_avg_yards_of_seperation  = models.FloatField(null=True, blank=True)
    old_top_speed= models.FloatField(null=True, blank=True)
    old_time_to_top_speed= models.FloatField(null=True, blank=True)