from django.shortcuts import render
from rest_framework import filters, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import SocialEngagement
from .serializers import SocialEngagementSerializer
import django_filters


class SocialPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class SocialEngagementViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing SocialEngagement of Player.
    create:
        Create a new SocialEngagement instance.
    retrieve:
        Return the given SocialEngagement.
    update:
        Update the given SocialEngagement.
    partial_update:
        Update the given SocialEngagement given field only.
    destroy:
        Delete the given SocialEngagement.
   """
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    pagination_class = SocialPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = SocialEngagementSerializer
    queryset = SocialEngagement.objects.all()

    filter_fields = {
        'id': ['exact', 'in'],
        'followers': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'following': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'tweets': ['iexact', 'icontains', 'istartswith', 'in', 'isnull']
    }
