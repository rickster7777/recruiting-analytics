import django_filters
from django.shortcuts import render
from django_filters.filterset import FilterSet, FilterSetMetaclass
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ra_user.models import User
from .models import Notifications
from .serializers import GETNotificationSerializer, NotificationSerializer
from datetime import datetime
import timeago
from django.utils import timezone
from django.utils.timezone import now,timedelta

# Create your views here.


class NotificationsPagination(pagination.PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class NotificationsViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing Notifications.
    create:
        Create a new Notifications instance.
    retrieve:
        Return the given Notifications.
    update:
        Update the given Notifications.
    partial_update:
        Update the given Notifications given field only.
    destroy:
        Delete the given Notifications.
   """
    pagination_class = NotificationsPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notifications.objects.all().order_by('-created_at')
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    ordering_fields = ('id',
                       'created_at'
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'user__id': ['iexact', 'in', 'icontains', 'istartswith'],
        'player__id': ['iexact', 'in', 'icontains', 'istartswith'],
        'read': ['isnull'],
        'notification_type': ['iexact', 'in', 'icontains', 'istartswith'],
        'created_at': ['iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'icontains', 'istartswith'],
    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GETNotificationSerializer
        else:
            return NotificationSerializer


    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if 'today' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=now().replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() + timedelta(days = 1)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')

        elif '1 day ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 1)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=now().replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '2 days ago' in  self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 2)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 1)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '3 days ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 3)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 2)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '4 days ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 4)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 3)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '5 days ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 5)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 4)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '6 days ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 6)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 5)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif '1 week ago' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__gte=(now() - timedelta(days = 7)).replace(hour=0,minute=0,second=0,microsecond = 0),
                created_at__lt=(now() - timedelta(days = 6)).replace(hour=0,minute=0,second=0,microsecond = 0)
                ).order_by('-created_at')
        elif 'earlier' in self.request.query_params:
            queryset = Notifications.objects.filter(
                user=self.request.user,
                created_at__lte=(now().replace(hour=0,minute=0,second=0,microsecond = 0) - timedelta(days = 7))
                ).order_by('-created_at')

        elif 'read_notifications' in self.request.query_params:
            queryset = Notifications.objects.filter(
                read=True,
                user=self.request.user
            ).order_by('-created_at')
        elif 'unread_notifications' in self.request.query_params:
            queryset = Notifications.objects.filter(
                read=False,
                user=self.request.user
            ).order_by('-created_at')
        elif 'user_id' in self.request.query_params:
            delete_ids = self.request.query_params.get(
                'user_id')
            notification_deletes = Notifications.objects.filter(
                user__id__iexact=delete_ids).delete()
            queryset = Notifications.objects.none()

        elif self.request.user.is_staff or 'admin' in user_group:
            queryset = Notifications.objects.all().order_by('-created_at')
            queryset = queryset.select_related('user', 'player')
        elif 'coach' in user_group:
            queryset = Notifications.objects.select_related('user', 'player').filter(
                user=self.request.user
            ).order_by('-created_at')
        else:
            queryset = Notifications.objects.none()

        return queryset


class NotificationsReportViewSet(viewsets.ViewSet):
    """
    list:
        Return a list of all the existing Notifications reports.
    """
    permission_classes = (IsAuthenticated,)

    def list(self, request):

        data = {}
        data['notifications'] = {

            'total': Notifications.objects.filter(
                user=self.request.user).count(),

            'read_notifications': Notifications.objects.filter(
                user=self.request.user,
                read=True).count(),

            'unread_notifications': Notifications.objects.filter(
                user=self.request.user,
                read=False).count(),


        }
        return Response(
            {
                'result': data
            })
