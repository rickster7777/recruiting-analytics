from django.db import models
from django.utils import timezone

# Create your models here.


class Notifications(models.Model):
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    Notification_Choices = (
        ("none", None),
        ("offers", "offers"),
        ("visits", "visits"),
        ("commit", "commit"),
        ("decommit", "decommit"),
    )
    notification_type = models.CharField(
        max_length=50,
        choices=Notification_Choices,
        default='none'
    )
    read = models.BooleanField(default=False)
    user = models.ForeignKey(
        'ra_user.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    player = models.ForeignKey(
        'players.Player',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
