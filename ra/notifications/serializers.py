import json
import math
from django.db.models import F, Q
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import Notifications
from ra_user.models import MyBoard, WatchList, User
from ra_user.serializers import GetUserSerializer
from players.serializers import GetPlayerSerializer
from players.models import Player
import timeago
from datetime import datetime, timezone,date
from django.utils.timezone import now,timedelta


class NotificationSerializer(serializers.ModelSerializer):
    """ Notifications model serializer """

    class Meta:
        model = Notifications
        fields = '__all__'


class UsersNotificationSerializer(serializers.ModelSerializer):
    """ User Notification Serializer """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email',
                  'groups', 'is_active', 'title', 'cell_phone', )
        read_only_fields = (fields, )
        depth = 1

class NotificationPlayerSerializer(serializers.ModelSerializer):
    """ NotificationUserSerializer model serializer for rendering required data """
    class Meta:
        model = Player
        fields = ('id', 'first_name', 'last_name', 'full_name', 'profile_photo',
                    )
        read_only_fields = (fields, )


class GETNotificationSerializer(serializers.ModelSerializer):
    """ Notifications model serializer """
    user = UsersNotificationSerializer(read_only=True)
    player = NotificationPlayerSerializer(read_only=True)
    notification_time = serializers.SerializerMethodField()
    class Meta:
        model = Notifications
        fields = '__all__'
        depth=1
        read_only_fields = (fields, )

    def get_notification_time(self,notification):
        notification_created = notification.created_at
        timeago_time = timeago.format(notification_created,now(),'UTC')
        d0 = date(now().year,now().month, now().day)
        d1 = date(notification_created.year,notification_created.month ,notification_created.day)
        creation_time = (d0 - d1).days
        #if now().day - notification_created.day == 0:
        if creation_time == 0:
            if 'second ago' in timeago_time:
                updated_time = timeago_time.replace('second','Sec')

            elif 'seconds ago' in timeago_time:
                updated_time = timeago_time.replace('seconds','Secs')

            elif 'minute ago' in timeago_time:
                updated_time = timeago_time.replace('minute','Min')

            elif 'minutes ago' in timeago_time:
                updated_time = timeago_time.replace('minutes','Mins')

            elif 'hour ago' in timeago_time:
                updated_time = timeago_time.replace('hour','Hour')

            elif 'hours ago' in timeago_time:
                updated_time = timeago_time.replace('hours','Hours')
            else:
                updated_time = ''

        #elif now().day - notification_created.day == 1:
        elif creation_time == 1:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 2:
        elif creation_time == 2:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 3:
        elif creation_time == 3:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 4:
        elif creation_time == 4:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 5:
        elif creation_time == 5:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 6:
        elif creation_time == 6:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day == 7:
        elif creation_time == 7:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)


        #elif now().day - notification_created.day > 7:
        elif creation_time > 7:
            month = notification_created.month
            year = notification_created.year
            day = notification_created.day
            updated_time = str(month) + '-' + str(day) + '-' + str(year)
        else:
            return None
        return updated_time
