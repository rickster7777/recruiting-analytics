from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from address.models import School, City, State, College
# from players.models import Player


class UserBillingAddress(models.Model):
    street = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City,
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    state = models.ForeignKey(State,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL)
    zip_code = models.CharField(max_length=20, blank=True, null=True)


class User(AbstractUser):
    """
    This model behaves identically to the auth user model, we are extending
    auth user model to add extra fields. In future we’ll be able to customize
    it if the further need arises.
    """
    email = models.EmailField(unique=True, null=False, blank=False)
    title = models.CharField(blank=True,
                             null=True, max_length=250)
    cell_phone = models.CharField(max_length=20, blank=True,
                                  null=True,)
    coach_address = models.ForeignKey(
        School,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    school_address = models.TextField(blank=True, null=True)
    privacy_and_policy = models.BooleanField(default=True)
    welcome_note = models.BooleanField(default=False)
    subscription = models.OneToOneField(
        'UserSubscription', null=True, blank=True, on_delete=models.SET_NULL
    )
    college_address = models.ForeignKey(
        'address.College',
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    save_search_names = ArrayField(
        models.CharField(max_length=200), null=True, blank=True)
    billing_address = models.ForeignKey(
        UserBillingAddress,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    offline = models.BooleanField(default=False)

    def __str__(self):
        return str(self.username) if self.username else ''


class UserOtp(models.Model):
    user = models.OneToOneField(User, null=True, blank=True,
                                on_delete=models.CASCADE)
    otp = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)
    expired_on = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """
        Overriding the save method to save updated_on data automatically
        Need to override created_by and updated_by from API as we don't have
        current user in save instance
        """

        if not self.pk:
            self.expired_on = timezone.now() + timezone.timedelta(minutes=15)
        else:
            self.expired_on = timezone.now() + timezone.timedelta(minutes=15)
            # self.expired_on = self.expired_on
        super(UserOtp, self).save(*args, **kwargs)


class UserSubscription(models.Model):
    customer_id = models.CharField(max_length=150, unique=True)
    subscription_id = models.CharField(max_length=150)
    plan = models.CharField(max_length=50, default='monthly')
    status = models.CharField(max_length=50)

    def __str__(self):
        return "Stripe Customer - {0}".format(self.customer_id)


class MyBoard(models.Model):
    user = models.ForeignKey(
        'ra_user.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    player = models.ForeignKey(
        'players.Player',
        # null=True,
        # blank=False,
        on_delete=models.CASCADE
    )
    added_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'player',)


class WatchList(models.Model):
    user = models.ForeignKey(
        'ra_user.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    player = models.ForeignKey(
        'players.Player',
        # null=True,
        # blank=False,
        on_delete=models.CASCADE
    )
    added_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'player',)
