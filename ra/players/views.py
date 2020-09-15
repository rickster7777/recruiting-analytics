import csv
import json
import math
import os
import urllib.request as urllib2

import django_filters
from django.core.files import File
from django.db import IntegrityError, models
from django.db.models import F, Max, Q
from django.http import Http404, StreamingHttpResponse
from django_filters.filterset import FilterSet, FilterSetMetaclass
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework.backends import utils
from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from address.models import City, School, State
from notifications.models import Notifications
from personality_insights.models import (PersonalityInsights, ProspectsNeeds,
                                         ProspectsPersonality, ProspectsValues)
from ra_user.models import MyBoard, User, WatchList
from social_engagement.models import SocialEngagement

from .models import (Classification, Comments, FbsDeCommit, FbsHardCommit,
                     FbsOffers, FbsSchools, Notes, Player, PlayerType,
                     PositionGroup, Positions, SavedSearch, SchoolsVisit,OldPlayMakingValues)
from .performance_data import get_athleticism, get_playmaking
from .highlighted_video import get_highlighted_video
from .permissions import (FixCommentsPermission,
                          FixFitfinderSavedSearchPermission)
from .serializers import (ClassificationSerializer, CommentSerializer,
                          FbsDeCommitSerializer, FbsHardCommitSerializer,
                          FbsOffersSerializer, FbsSchoolsSerializer,
                          GetCommentSerializer, GetFbsHardCommitSerializer,
                          GetFbsOffersSerializer, GETFbsSchoolsSerializer,
                          GetNotesSerializer, GetPlayerSerializer,
                          GetPositionSerializer, GetSavedSearchSerializer,
                          GetSchoolsVisitSerializer, NotesSerializer,
                          PlayerSerializer, PlayerTypeSerializer,
                          PositionGroupSerializer, PositionsSerializer,
                          PostNotesSerializer, SavedSearchSerializer,
                          SchoolsVisitSerializer)


class FbsSchoolsViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing position group.
    create:
        Create a new position group instance.
    retrieve:
        Return the given position group.
    update:
        Update the given position group.
    partial_update:
        Update the given position group given field only.
    destroy:
        Delete the given position group.
   """
    permission_classes = (IsAuthenticated,)
    serializer_class = FbsSchoolsSerializer
    queryset = FbsSchools.objects.all()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'status': ['iexact', 'in', 'icontains', 'isnull'],
    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GETFbsSchoolsSerializer
        else:
            return FbsSchoolsSerializer


class PlayerPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class CommentsViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing Comments.
    create:
        Create a new Comments instance.
    retrieve:
        Return the given Comments.
    update:
        Update the given Comments.
    partial_update:
        Update the given Comments given field only.
    destroy:
        Delete the given Comments.
   """
    pagination_class = PlayerPagination
    permission_classes = (IsAuthenticated, FixCommentsPermission)
    serializer_class = CommentSerializer
    queryset = Comments.objects.all()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    ordering_fields = ('id',
                       'commented_by__username',
                       'created_at',
                       'updated_on',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'commented_by__username': ['iexact', 'in', 'icontains', 'istartswith'],

    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetCommentSerializer
        else:
            return CommentSerializer

    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.user.is_staff or 'admin' in user_group:
            queryset = Comments.objects.all()

        elif 'coach' in user_group:
            if self.request.query_params.get('note_id'):
                note_id = self.request.query_params.get('note_id')
                notes_comment = Notes.objects.filter(id__iexact=note_id).values_list(
                    'comments__id', flat=True
                )
                filters = {}
                filters['commented_by__college_address__isnull'] = False
                queryset = Comments.objects.filter(
                    **filters,
                    id__in=notes_comment,
                    commented_by__college_address__name=self.request.user.college_address.name
                ).order_by('created_at')
            else:
                filters = {}
                filters['commented_by__college_address__isnull'] = False
                queryset = Comments.objects.filter(
                    **filters,
                    commented_by__college_address__name=self.request.user.college_address.name
                ).order_by('created_at')
        else:
            queryset = Comments.objects.none()

        return queryset

    def perform_create(self, serializer):
        note_id = self.request.data['note_id']
        message = self.request.data['message']
        commented_by = self.request.user
        new_comment = Comments()
        new_comment.message = message
        new_comment.commented_by = commented_by
        new_comment.save()
        note = Notes.objects.get(id=note_id)
        note.comments.add(new_comment)

    def perform_update(self, serializer):
        serializer.save(commented_by=self.request.user)


class FbsDeCommitViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing FbsDeCommit.
    create:
        Create a new FbsDeCommit instance.
    retrieve:
        Return the given FbsDeCommit.
    update:
        Update the given FbsDeCommit.
    partial_update:
        Update the given FbsDeCommit given field only.
    destroy:
        Delete the given FbsDeCommit.
   """
    permission_classes = (IsAuthenticated,)
    serializer_class = FbsDeCommitSerializer
    queryset = FbsDeCommit.objects.all()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    ordering_fields = ('id',
                       'school__name',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'school__name': ['iexact', 'in', 'icontains', 'istartswith']
    }


class PlayerPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class CustomOrderingFilter(filters.OrderingFilter):
    """ Use nulls_last feature to force nulls to bottom in all orderings. """

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset


class PlayerViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing players.
    create:
        Create a new player instance.
    retrieve:
        Return the given player.
    update:
        Update the given player.
    partial_update:
        Update the given player given field only.
    destroy:
        Delete the given player.
   """
    pagination_class = PlayerPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerSerializer
    queryset = Player.objects.all().distinct()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, CustomOrderingFilter,
    )

    ordering_fields = ('id',
                       'first_name',
                       'last_name',
                       'full_name',
                       'height',
                       'weight',
                       'film_grade',
                       'athleticism',
                       'play_making',
                       'classification__year',
                       'top_speed',
                       'role__name',
                       'position__name',
                       'position__group__name',
                       'rank',
                       'priority',
                       'fourty_yard_dash',
                       'short_shuttle',
                       'vertical',
                       'school__name',
                       'state__name',
                       'city__name',
                       )

    filter_fields = {
        'id': ['exact', 'in'],
        'first_name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__region__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'city__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'city__state__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__region': ['isnull'],
        'school__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'last_name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'full_name': ['iexact', 'icontains', 'istartswith', 'startswith', 'in', 'isnull'],
        'height': ['iexact', 'icontains', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'weight': ['iexact', 'lt', 'gt', 'lte', 'gte', 'istartswith', 'isnull', 'iexact', 'in'],
        'fourty_yard_dash': ['iexact', 'icontains', 'startswith', 'lt', 'lte', 'gt', 'gte',
                             'istartswith', 'isnull', 'iexact', 'in'],
        'star_rating': ['iexact', 'icontains', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'short_shuttle': ['iexact', 'icontains', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'vertical': ['iexact', 'icontains', 'istartswith', 'isnull', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'hundred_yard_dash': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'twitter_handle': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'jersey_number': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'role__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'school__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'position__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        # 'position': ['isnull'],
        'position__group__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'classification__year': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'film_grade': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'athleticism': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'play_making': ['iexact', 'icontains', 'istartswith', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'top_speed': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'rank': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'fbs_offers': ['isnull'],
        'priority': ['iexact', 'icontains', 'in', 'lt', 'gt', 'lte', 'gte', 'isnull'],
        'notes__created_by__username': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'notes__created_by__email': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'play_making_raw_score': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'last_twitter_status': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'personality_insight': ['isnull'],
        'personality_insight__personality__team_player': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'social_engagement': ['isnull'],
        'avg_transition_time': ['isnull'],
        'avg_yards_of_seperation': ['isnull'],
        'time_to_top_speed': ['isnull'],
        'video_highlight': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'fbs_offers__schools': ['isnull'],
        'sack': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'interception': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'touchdown': ['iexact', 'icontains', 'istartswith', 'lt', 'gt', 'lte', 'gte', 'in', 'isnull'],
        'video_highlight_duration': ['isnull', ],
        'classification': ['isnull', ],
        'position__group__status': ['iexact', 'icontains', 'istartswith', 'in', ],
        'position__groups__status': ['iexact', 'icontains', 'istartswith', 'in', ],
        'position__groups__name': ['iexact', 'icontains', 'istartswith', 'in', ],
        'position__groups__detailed_name': ['iexact', 'icontains', 'istartswith', 'in', ],
        'position__group__detailed_name': ['iexact', 'icontains', 'istartswith', 'in', ],

    }

    def get_queryset(self):
        if self.request.query_params.get('delete_players'):
            player_ids = self.request.query_params.get('delete_players')
            ids = player_ids.split(',')
            for player_id in ids:
                player_notifications = Notifications.objects.filter(
                    player__id=player_id
                ).delete()
                player_myboard = MyBoard.objects.filter(
                    player__id=player_id
                ).delete()
                player_watchlist = WatchList.objects.filter(
                    player__id=player_id
                ).delete()
            players = Player.objects.filter(id__in=ids).delete()
            queryset = Player.objects.none()
        if self.request.query_params.get('nfl_id'):
            nfl_id = self.request.query_params.get('nfl_id')
            nfl_player = Player.objects.filter(
                id=nfl_id)
            if nfl_player:
                if nfl_player[0].film_grade != None and nfl_player[0].weight != None and nfl_player[0].height != None:
                    nfl_filmgrade = nfl_player[0].film_grade
                    nfl_height = nfl_player[0].height
                    nfl_weight = nfl_player[0].weight
                    filters = {}
                    filters['film_grade__isnull'] = False
                    filters['height__isnull'] = False
                    filters['weight__isnull'] = False

                    for filter in self.request.query_params:
                        if filter == 'classification__year__iexact':
                            filters['classification__year__iexact'] = self.request.query_params['classification__year__iexact']
                        if filter == 'position__groups__name__iexact':
                            filters['position__groups__name__iexact'] = self.request.query_params['position__groups__name__iexact']
                        # if filter == 'role__name__in':
                            # filters['role__name__in'] = self.request.query_params['role__name__in']

                    queryset = Player.objects.select_related(
                        'role', 'school', 'classification', 'city', 'state',
                        'personality_insight', 'fbs_offers',
                        'social_engagement', )\
                        .prefetch_related('notes', 'position')\
                        .filter(
                        Q(
                            Q(**filters) &
                            Q(role__name='undercruited') &
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
                else:
                    queryset = Player.objects.none()

        elif self.request.query_params.get('uc_id'):
            uc_id = self.request.query_params.get('uc_id')
            if uc_id is not None:
                uc_player = Player.objects.filter(id=uc_id)
                filters = {}
                if uc_player[0].film_grade != None and uc_player[0].weight != None and uc_player[0].height != None:
                    uc_filmgrade = uc_player[0].film_grade
                    uc_height = uc_player[0].height
                    uc_weight = uc_player[0].weight
                    filters['film_grade__isnull'] = False
                    filters['height__isnull'] = False
                    filters['weight__isnull'] = False
                    filters['role__name__iexact'] = 'nfl'

                    queryset = Player.objects.filter(
                        Q(
                            Q(**filters) &
                            Q(film_grade__lte=uc_filmgrade + 3.0) &
                            Q(film_grade__gte=uc_filmgrade - 3.0)
                        ) &
                        Q(
                            (
                                Q(height__lte=uc_height + 1) &
                                Q(height__gte=uc_height - 1)
                            ) &
                            (
                                Q(weight__lte=uc_weight + 15.0) &
                                Q(weight__gte=uc_weight - 15.0)
                            )
                        )
                    ).distinct()
                else:
                    queryset = Player.objects.none()
        else:
            queryset = Player.objects.all().distinct()
            queryset = self.get_serializer_class().setup_eager_loading(
                queryset)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetPlayerSerializer
        else:
            return PlayerSerializer

    def retrieve(self, request, *args, **kwargs):
        player = self.get_object()
        if self.request.query_params.get('delete_notes') == 'true':
            notes = Notes.objects.filter(id__in=player.notes.all())
            notes.delete()
        if self.request.query_params.get('fbs_schools') == 'old':
            if player.fbs_offers != None:
                fbs_id = player.fbs_offers.id
                fbs_schools_objs = FbsSchools.objects.select_related('fbs_offer', 'school').filter(
                    fbs_offer__id=fbs_id
                ).update(status='old')

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=self.kwargs["pk"])
            player_notifications = Notifications.objects.filter(
                player__id__iexact=str(player.id)).delete()
            player_myboard = MyBoard.objects.filter(
                player__id=str(player.id)
            ).delete()
            player_watchlist = WatchList.objects.filter(
                player__id=str(player.id)
            ).delete()
            player.delete()
            return Response(status.HTTP_200_OK)
        except:
            return Response("Player not found")


class PlayerTypeViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing player type.
    create:
        Create a new player type instance.
    retrieve:
        Return the given player type.
    update:
        Update the given player type.
    partial_update:
        Update the given player type given field only.
    destroy:
        Delete the given player type.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = PlayerTypeSerializer
    queryset = PlayerType.objects.all().order_by('name').distinct()


class NotesViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing notes.
    create:
        Create a new player type instance.
    retrieve:
        Return the given notes type.
    update:
        Update the given notes type.
    partial_update:
        Update the given notes type given field only.
    destroy:
        Delete the given notes type.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    filter_fields = {
        'id': ['exact', 'in'],
        'created_by__email': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'created_by__username': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetNotesSerializer
        elif self.request.method in ['POST']:
            return PostNotesSerializer
        else:
            return NotesSerializer

    # def create(self, request):
    #     serializer = NotesSerializer(data=request.data)

    #     if serializer.is_valid():
    #         serializer.save()
    #         player_id = request.data['player_id']
    #         if player_id:
    #             player = Player.objects.filter(id=player_id)
    #             if player:
    #                 note = Notes.objects.get(title=request.data['title'])
    #                 player[0].notes.add(note.id)
    #         note = Notes.objects.get(title=request.data['title'])
    #         player_id = self.request.query_params.get('player_id')
    #         if player_id:
    #             player = Player.objects.get(id=player_id)
    #             player.notes.add(note.id)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.user.is_staff or 'admin' in user_group:
            queryset = Notes.objects.all()

        elif 'coach' in user_group:
            if ('note_id' and 'comment_ids') in self.request.query_params:
                note_id = self.request.query_params.get('note_id')
                Notes.objects.get(id=note_id).delete()
                comment_ids = self.request.query_params.get(
                    'comment_ids').split(',')
                Comments.objects.filter(id__in=comment_ids).delete()
                queryset = Notes.objects.none()
            elif self.request.query_params.get('player_id'):
                player_id = self.request.query_params.get('player_id')
                player_notes = Player.objects.filter(id__iexact=player_id).values_list(
                    'notes__id', flat=True
                )
                filters = {}
                filters['created_by__college_address__isnull'] = False
                queryset = Notes.objects.select_related(
                    'created_by').prefetch_related('comments').filter(
                    **filters,
                    id__in=player_notes,
                    created_by__college_address__name=self.request.user.college_address.name
                ).order_by('-created_on')
            else:
                queryset = Notes.objects.select_related(
                    'created_by').prefetch_related('comments').filter(
                    created_by__college_address=self.request.user.college_address
                )
        else:
            queryset = Notes.objects.none()

        return queryset

    def perform_create(self, serializer):
        player_id = self.request.data['player_id']
        title = self.request.data['title']
        description = self.request.data['description']
        # comments = self.request.data['comments']
        created_by = self.request.user
        user = User.objects.get(id=self.request.user.id)
        new_note = Notes()
        new_note.title = title
        new_note.description = description
        # new_note.comments = comments
        new_note.created_by = user
        new_note.save()
        player = Player.objects.get(id=player_id)
        player.notes.add(new_note)

    def perform_update(self, serializer):
        user = User.objects.get(id=self.request.user.id)
        serializer.save(created_by=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassificationViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing classification.
    create:
        Create a new classification instance.
    retrieve:
        Return the given classification type.
    update:
        Update the given classification type.
    partial_update:
        Update the given classification type given field only.
    destroy:
        Delete the given classification type.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = ClassificationSerializer
    queryset = Classification.objects.all().order_by('year').distinct()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )
    ordering_fields = ('id',
                       'year',
                       )
    filter_fields = {
        'id': ['iexact', 'in', ],
        'year': ['iexact', 'in', 'icontains', 'isnull', 'istartswith'],
    }


class PositionsViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing positions.
    create:
        Create a new positions instance.
    retrieve:
        Return the given positions.
    update:
        Update the given positions.
    partial_update:
        Update the given positions given field only.
    destroy:
        Delete the given positions.
   """
    permission_classes = (IsAuthenticated,)
    serializer_class = PositionsSerializer
    queryset = Positions.objects.all().order_by('name').distinct()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name',
                       'group__name',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'name': ['iexact', 'in', 'icontains', 'istartswith'],
        'group__name': ['iexact', 'in', 'icontains', 'istartswith'],
        'group__status': ['iexact', 'in', 'icontains', 'istartswith'],
        'groups__status': ['iexact', 'in', 'icontains', 'istartswith'],
        'groups__detailed_name': ['iexact', 'in', 'icontains', 'istartswith'],
        'group__detailed_name': ['iexact', 'in', 'icontains', 'istartswith'],
        'groups__name': ['iexact', 'in', 'icontains', 'istartswith'],

    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetPositionSerializer
        else:
            return PositionsSerializer


class PositionGroupViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing position group.
    create:
        Create a new position group instance.
    retrieve:
        Return the given position group.
    update:
        Update the given position group.
    partial_update:
        Update the given position group given field only.
    destroy:
        Delete the given position group.
   """
    permission_classes = (IsAuthenticated,)
    serializer_class = PositionGroupSerializer
    queryset = PositionGroup.objects.all().order_by('name').distinct()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'name': ['iexact', 'in', 'icontains', 'istartswith'],
        'status': ['iexact', 'in', 'icontains', 'istartswith'],
        'detailed_name': ['iexact', 'in', 'icontains', 'istartswith'],
    }


# class UndercruitedPlayersViewSet(viewsets.ViewSet):
#     """
#     list:
#         Return a list of all the existing reports.
#    """

#     def list(self, request):

#         data = {}
#         uc_players = Player.objects.filter(role__name='Undercruited')
#         for player in uc_players:

#             data[player.first_name] = {
#                 'Player': Player.objects.filter(
#                     first_name=player.first_name).values(),
#                 'FilmGrade': player.film_grade,
#                 'Athleticism': player.athleticism,
#                 'play_making': player.play_making,
#             }

#         return Response(data)


class SchoolsVisitViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing SchoolsVisit of Player.
    create:
        Create a new SchoolsVisit instance.
    retrieve:
        Return the given SchoolsVisit.
    update:
        Update the given SchoolsVisit.
    partial_update:
        Update the given SchoolsVisit given field only.
    destroy:
        Delete the given SchoolsVisit.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolsVisitSerializer
    queryset = SchoolsVisit.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetSchoolsVisitSerializer
        else:
            return SchoolsVisitSerializer


class FbsHardCommitViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing FbsHardCommit of Player.
    create:
        Create a new FbsHardCommit instance.
    retrieve:
        Return the given FbsHardCommit.
    update:
        Update the given FbsHardCommit.
    partial_update:
        Update the given FbsHardCommit given field only.
    destroy:
        Delete the given FbsHardCommit.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = FbsHardCommitSerializer
    queryset = FbsHardCommit.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetFbsHardCommitSerializer
        else:
            return FbsHardCommitSerializer


class FbsOffersPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class FbsOffersViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing FbsOffers of Player.
    create:
        Create a new FbsOffers instance.
    retrieve:
        Return the given FbsOffers.
    update:
        Update the given FbsOffers.
    partial_update:
        Update the given FbsOffers given field only.
    destroy:
        Delete the given FbsOffers.
   """
    pagination_class = FbsOffersPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = FbsOffersSerializer
    queryset = FbsOffers.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetFbsOffersSerializer
        else:
            return FbsOffersSerializer


class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing SavedSearch of FitFinder.
    create:
        Create a new SavedSearch instance.
    retrieve:
        Return the given SavedSearch.
    update:
        Update the given SavedSearch.
    partial_update:
        Update the given SavedSearch given field only.
    destroy:
        Delete the given SavedSearch.
   """

    permission_classes = (IsAuthenticated, FixFitfinderSavedSearchPermission)
    # pagination_class = PlayerPagination
    serializer_class = SavedSearchSerializer
    queryset = SavedSearch.objects.all()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name',
                       )
    filter_fields = {
        'id': ['exact', 'in'],
        'name': ['iexact', 'icontains', 'istartswith', 'isnull', 'in'],
        'search_by__username': ['iexact', 'icontains', 'istartswith', 'isnull', 'in'],
        'search_by__id': ['iexact', 'icontains', 'istartswith', 'isnull', 'in'],
    }

    def get_queryset(self):
        user_group = User.objects.filter(
            username=self.request.user
        ).values_list('groups__name', flat=True)

        if self.request.user.is_staff or 'admin' in user_group:

            queryset = SavedSearch.objects.all()

        elif 'coach' in user_group:
            queryset = SavedSearch.objects.filter(
                search_by=self.request.user)
        else:
            queryset = SavedSearch.objects.none()

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetSavedSearchSerializer
        else:
            return SavedSearchSerializer

    def perform_create(self, serializer):
        serializer.save(search_by=self.request.user)


class PerformanceRankingViewSet(viewsets.ViewSet):
    """
    list:
        Return a list of all the counts of all ranking for Performance data.
    """

    def list(self, request):
        film_grade_rank = 0
        out_of_film_grade = 0
        playmaking_rank = 0
        out_of_playmaking = 0
        athleticism_rank = 0
        out_of_athleticism = 0
        film_grade_rank = 0
        out_of_filmgrade = 0
        avg_transition_time_rank = 0
        out_of_avg_transition_time = 0
        avg_closing_speed_rank = 0
        out_of_avg_closing_speed = 0
        avg_yards_of_seperation_rank = 0
        out_of_avg_yards_of_seperation = 0
        max_speed_rank = 0
        out_of_max_speed = 0
        time_to_top_speed_rank = 0
        out_of_time_to_top_speed = 0
        sack_rank = 0
        out_of_sack = 0
        interception_rank = 0
        out_of_interception = 0
        touchdown_rank = 0
        out_of_touchdown = 0
        if self.request.query_params.get('player_id'):
            print("succ")
            player = Player.objects.get(
                id=self.request.query_params.get('player_id'))
            if player.play_making != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        play_making__isnull=False
                    ).order_by(
                        F('play_making').desc(nulls_last=True))
                    list_obj = list(players)
                    playmaking_rank = list_obj.index(player) + 1
                    out_of_playmaking = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        play_making__isnull=False
                    ).order_by(
                        F('play_making').desc(nulls_last=True))
                    list_obj = list(players)
                    playmaking_rank = list_obj.index(player) + 1
                    out_of_playmaking = len(players)
                elif cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        play_making__isnull=False
                    ).order_by(
                        F('play_making').desc(nulls_last=True))
                    list_obj = list(players)
                    playmaking_rank = list_obj.index(player) + 1
                    out_of_playmaking = len(players)
            if player.athleticism != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        athleticism__isnull=False
                    ).order_by(
                        F('athleticism').desc(nulls_last=True))
                    list_obj = list(players)
                    athleticism_rank = list_obj.index(player) + 1
                    out_of_athleticism = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        athleticism__isnull=False
                    ).order_by(
                        F('athleticism').desc(nulls_last=True))
                    list_obj = list(players)
                    athleticism_rank = list_obj.index(player) + 1
                    out_of_athleticism = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        athleticism__isnull=False
                    ).order_by(
                        F('athleticism').desc(nulls_last=True))
                    list_obj = list(players)
                    athleticism_rank = list_obj.index(player) + 1
                    out_of_athleticism = len(players)
            if player.film_grade != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        film_grade__isnull=False
                    ).order_by(
                        F('film_grade').desc(nulls_last=True))
                    list_obj = list(players)
                    film_grade_rank = list_obj.index(player) + 1
                    out_of_film_grade = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        film_grade__isnull=False
                    ).order_by(
                        F('film_grade').desc(nulls_last=True))
                    list_obj = list(players)
                    film_grade_rank = list_obj.index(player) + 1
                    out_of_film_grade = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        film_grade__isnull=False
                    ).order_by(
                        F('film_grade').desc(nulls_last=True))
                    list_obj = list(players)
                    film_grade_rank = list_obj.index(player) + 1
                    out_of_film_grade = len(players)

            if player.avg_transition_time != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        avg_transition_time__isnull=False
                    ).order_by(
                        F('avg_transition_time').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_transition_time_rank = list_obj.index(player) + 1
                    out_of_avg_transition_time = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        avg_transition_time__isnull=False
                    ).order_by(
                        F('avg_transition_time').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_transition_time_rank = list_obj.index(player) + 1
                    out_of_avg_transition_time = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        avg_transition_time__isnull=False
                    ).order_by(
                        F('avg_transition_time').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_transition_time_rank = list_obj.index(player) + 1
                    out_of_avg_transition_time = len(players)
            if player.avg_closing_speed != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        avg_closing_speed__isnull=False
                    ).order_by(
                        F('avg_closing_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_closing_speed_rank = list_obj.index(player) + 1
                    out_of_avg_closing_speed = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        avg_closing_speed__isnull=False
                    ).order_by(
                        F('avg_closing_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_closing_speed_rank = list_obj.index(player) + 1
                    out_of_avg_closing_speed = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        avg_closing_speed__isnull=False
                    ).order_by(
                        F('avg_closing_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_closing_speed_rank = list_obj.index(player) + 1
                    out_of_avg_closing_speed = len(players)
            if player.avg_yards_of_seperation != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        avg_yards_of_seperation__isnull=False
                    ).order_by(
                        F('avg_yards_of_seperation').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_yards_of_seperation_rank = list_obj.index(player) + 1
                    out_of_avg_yards_of_seperation = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        classification__year='2020',
                        avg_yards_of_seperation__isnull=False
                    ).order_by(
                        F('avg_yards_of_seperation').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_yards_of_seperation_rank = list_obj.index(player) + 1
                    out_of_avg_yards_of_seperation = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        avg_yards_of_seperation__isnull=False
                    ).order_by(
                        F('avg_yards_of_seperation').asc(nulls_last=True))
                    list_obj = list(players)
                    avg_yards_of_seperation_rank = list_obj.index(player) + 1
                    out_of_avg_yards_of_seperation = len(players)
            if player.top_speed != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        top_speed__isnull=False
                    ).order_by(
                        F('top_speed').desc(nulls_last=True))
                    list_obj = list(players)
                    max_speed_rank = list_obj.index(player) + 1
                    out_of_max_speed = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        top_speed__isnull=False
                    ).order_by(
                        F('top_speed').desc(nulls_last=True))
                    list_obj = list(players)
                    max_speed_rank = list_obj.index(player) + 1
                    out_of_max_speed = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        top_speed__isnull=False
                    ).order_by(
                        F('top_speed').desc(nulls_last=True))
                    list_obj = list(players)
                    max_speed_rank = list_obj.index(player) + 1
                    out_of_max_speed = len(players)
            if player.time_to_top_speed != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        time_to_top_speed__isnull=False
                    ).order_by(
                        F('time_to_top_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    time_to_top_speed_rank = list_obj.index(player) + 1
                    out_of_time_to_top_speed = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        time_to_top_speed__isnull=False
                    ).order_by(
                        F('time_to_top_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    time_to_top_speed_rank = list_obj.index(player) + 1
                    out_of_time_to_top_speed = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        time_to_top_speed__isnull=False
                    ).order_by(
                        F('time_to_top_speed').asc(nulls_last=True))
                    list_obj = list(players)
                    time_to_top_speed_rank = list_obj.index(player) + 1
                    out_of_time_to_top_speed = len(players)
            if player.sack != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        sack__isnull=False
                    ).order_by(
                        F('sack').desc(nulls_last=True))
                    list_obj = list(players)
                    sack_rank = list_obj.index(player) + 1
                    out_of_sack = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        sack__isnull=False
                    ).order_by(
                        F('sack').desc(nulls_last=True))
                    list_obj = list(players)
                    sack_rank = list_obj.index(player) + 1
                    out_of_sack = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        sack__isnull=False
                    ).order_by(
                        F('sack').desc(nulls_last=True))
                    list_obj = list(players)
                    sack_rank = list_obj.index(player) + 1
                    out_of_sack = len(players)
            if player.interception != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        interception__isnull=False
                    ).order_by(
                        F('interception').desc(nulls_last=True))
                    list_obj = list(players)
                    interception_rank = list_obj.index(player) + 1
                    out_of_interception = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        interception__isnull=False
                    ).order_by(
                        F('interception').desc(nulls_last=True))
                    list_obj = list(players)
                    interception_rank = list_obj.index(player) + 1
                    out_of_interception = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        interception__isnull=False
                    ).order_by(
                        F('interception').desc(nulls_last=True))
                    list_obj = list(players)
                    interception_rank = list_obj.index(player) + 1
                    out_of_interception = len(players)
            if player.touchdown != None and player.classification != None:
                cls_year = player.classification.year
                if cls_year == '2021':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2021',
                        touchdown__isnull=False
                    ).order_by(
                        F('touchdown').desc(nulls_last=True))
                    list_obj = list(players)
                    touchdown_rank = list_obj.index(player) + 1
                    out_of_touchdown = len(players)
                elif cls_year == '2020':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2020',
                        touchdown__isnull=False
                    ).order_by(
                        F('touchdown').desc(nulls_last=True))
                    list_obj = list(players)
                    touchdown_rank = list_obj.index(player) + 1
                    out_of_touchdown = len(players)
                if cls_year == '2022':
                    players = Player.objects.filter(
                        role__name__in=['prospect', 'undercruited'],
                        classification__year='2022',
                        touchdown__isnull=False
                    ).order_by(
                        F('touchdown').desc(nulls_last=True))
                    list_obj = list(players)
                    touchdown_rank = list_obj.index(player) + 1
                    out_of_touchdown = len(players)

        Results = {}

        Results['performance_ranking'] = {
            'film_grade_rank': film_grade_rank,
            'out_of_film_grade': out_of_film_grade,
            'athleticism_rank': athleticism_rank,
            'out_of_athleticism': out_of_athleticism,
            'playmaking_rank': playmaking_rank,
            'out_of_playmaking': out_of_playmaking,
            'avg_transition_time_rank': avg_transition_time_rank,
            'out_of_avg_transition_time': out_of_avg_transition_time,
            'avg_closing_speed_rank': avg_closing_speed_rank,
            'out_of_avg_closing_speed': out_of_avg_closing_speed,
            'avg_yards_of_seperation_rank': avg_yards_of_seperation_rank,
            'out_of_avg_yards_of_seperation': out_of_avg_yards_of_seperation,
            'max_speed_rank': max_speed_rank,
            'out_of_max_speed': out_of_max_speed,
            'time_to_top_speed_rank': time_to_top_speed_rank,
            'out_of_time_to_top_speed': out_of_time_to_top_speed,
            'interception_rank': interception_rank,
            'out_of_interception': out_of_interception,
            'sack_rank': sack_rank,
            'out_of_sack': out_of_sack,
            'touchdown_rank': touchdown_rank,
            'out_of_touchdown': out_of_touchdown,
        }
        return Response(Results)


# Custom API for Update and Create an Individual Player

@api_view(['GET', 'POST', 'PUT'])
def player_update_view(request):
    print('succ')
    if request.method == 'GET':
        print('GET Method')
    if request.method == 'POST':
        print('Post Method')
        firstname = request.data['first_name']
        lastname = request.data['last_name']
        fullname = firstname + ' ' + lastname
        player = Player.objects.create(first_name=firstname.title().strip(),
                                       last_name=lastname.title().strip(),
                                       full_name=fullname)

        player_role = PlayerType.objects.get(name__iexact="prospect")
        player.role = player_role

        p_avatar = request.data['profile_photo']
        if p_avatar != None:
            p_avatar = request.data['profile_photo']
            result = urllib2.urlretrieve(p_avatar)
            player.profile_photo.save(
                os.path.basename(
                    player.full_name + '.png'),
                File(open(result[0], 'rb'))
            )
        else:
            player.profile_photo = None

        p_height = request.data['height']
        p_weight = request.data['weight']
        p_city = request.data['city']
        p_vertical = request.data['vertical']
        p_fourty_yard_dash = request.data['fourty_yard_dash']
        p_short_shuttle = request.data['short_shuttle']
        if 'video_highlight' in request.data:
            #player.video_highlight = request.data['video_highlight']
            url = request.data['video_highlight']
            if url != '' and url != None:
                get_highlighted_video(player,url)
            else:
                player.video_highlight = None

        else:
            player.video_highlight = None

        if p_city != None and p_city != '':
            player_city = p_city['name']
        else:
            player_city = None
        p_state = request.data['state']
        if p_state != None and p_state != '':
            player_state = p_state['name']
        else:
            player_state = None
        p_school = request.data['school']
        if p_school != None and p_school != '':
            player_school = p_school['name']
        else:
            player_school = None

        p_class = request.data['classification']
        if p_class != None and p_class != '':
            player_class = p_class['year']
        else:
            player_class = None
        p_positions = request.data['position']
        p_avg_transition_time = request.data['avg_transition_time']
        p_avg_closing_speed = request.data['avg_closing_speed']
        p_avg_yards_of_seperation = request.data['avg_yards_of_seperation']
        p_top_speed = request.data['top_speed']
        p_time_to_top_speed = request.data['time_to_top_speed']
        p_sack = request.data['sack']
        p_interception = request.data['interception']
        p_touchdown = request.data['touchdown']
        # FBS Offers
        p_fbs_offer = request.data['fbs_offers']
        if p_fbs_offer:
            p_decommit = p_fbs_offer['decommit']
            # Decommit
            if p_decommit:
                p_decommit_date = p_decommit['decommited_on']
                if p_decommit_date:
                    decommit_date = p_decommit_date
                else:
                    decommit_date = None
                p_decommit_school = p_decommit['school']
                if p_decommit_school:
                    decommit_school = p_decommit_school['name']
            else:
                decommit_date = None
                decommit_school = None

        # Hard Commit
        p_commit = p_fbs_offer['hard_commit']
        if p_commit:
            p_commit_date = p_commit['commited_on']
            if p_commit_date:
                commit_date = p_commit_date
            else:
                commit_date = None
            p_commit_school = p_commit['school']
            if p_commit_school:
                commit_school = p_commit_school['name']
        else:
            commit_date = None
            commit_school = None

        # Visits
        p_visits = p_fbs_offer['visits']
        if p_visits:
            school_visits = []
            for school_nm in p_visits['schools']:
                nm = school_visits.append(school_nm)
        else:
            school_visits = []
        if p_fbs_offer:
            fbs_schools = []
            p_fbs_schools = p_fbs_offer['schools']
            for school_nm in p_fbs_schools:
                nm = fbs_schools.append(school_nm)
        else:
            fbs_schools = []

        # Fbs Offers
        fbs_obj = None
        hard_commit_obj = None
        decommit_obj = None
        if len(fbs_schools) >= 1:
            fbs_obj = FbsOffers.objects.create(
                total=len(fbs_schools))
            fbs_schools_objs = School.objects.filter(
                name__in=fbs_schools)
            for school_obj in fbs_schools_objs:
                fbs_obj.schools.add(school_obj.id)
            fbs_obj.save()
            player.fbs_offers = fbs_obj
        if p_commit != None:
            hard_commit_sch = None
            try:
                if commit_school != None:
                    hard_commit_sch = School.objects.get(
                        name__iexact=commit_school)
            except School.DoesNotExist:
                if commit_school != None:
                    hard_commit_sch = School.objects.create(
                        name=commit_school)
            # if commit_school != None:
            if hard_commit_sch != None:
                hard_commit_obj = FbsHardCommit.objects.create(
                    school=hard_commit_sch)
                if commit_date != None:
                    hard_commit_obj.commited_on = commit_date
                    hard_commit_obj.save()
                    if fbs_obj != None:
                        fbs_obj.hard_commit = hard_commit_obj
                        fbs_obj.save()
                    else:
                        fbs_obj = FbsOffers.objects.create(
                            hard_commit=hard_commit_obj)
                        player.fbs_offers = fbs_obj

        if p_decommit != None:
            decommit_sch = None
            try:
                if decommit_school != None:
                    decommit_sch = School.objects.get(
                        name__iexact=decommit_school)
            except School.DoesNotExist:
                if decommit_school != None:
                    decommit_sch = School.objects.create(
                        name=decommit_school)
            # if commit_school != None:
            if decommit_school != None:
                decommit_obj = FbsDeCommit.objects.create(
                    school=decommit_sch)
                if decommit_date != None:
                    decommit_obj.decommited_on = decommit_date
                    decommit_obj.save()
                    if fbs_obj != None:
                        fbs_obj.decommit = decommit_obj
                        fbs_obj.save()
                        player.fbs_offers = fbs_obj
                    else:
                        fbs_obj = FbsOffers.objects.create(
                            decommit=decommit_obj)
                        player.fbs_offers = fbs_obj

            if len(school_visits) >= 1:
                # if fbs_obj == None:
                visits_obj = SchoolsVisit.objects.create(
                    total=len(school_visits))
                visit_schools_objs = School.objects.filter(
                    name__in=school_visits)
                for school_obj in visit_schools_objs:
                    visits_obj.schools.add(school_obj.id)
                if fbs_obj != None:
                    fbs_obj.visits = visits_obj
                    fbs_obj.save()
                    player.fbs_offers = fbs_obj

                else:
                    fbs_obj = FbsOffers.objects.create(
                        visits=visits_obj)
                    player.fbs_offers = fbs_obj

        if player.height:
            if p_height != None and p_height != '':
                if len(p_height) == 1:
                    feet = int(height_val)
                    inches = 0
                    player_height = (feet*12 + inches)
                    player.height = player_height
                else:
                    if len(p_height) >= 3:
                        list_obj = p_height.split('.')
                        feet = int(list_obj[0])
                    if len(list_obj) >= 2:
                        inches = int(list_obj[1])
                    else:
                        inches = 0
                    player_height = (feet*12 + inches)
                    player.height = player_height
        p_avatar = request.data['profile_photo']
        if player.profile_photo:
            if p_avatar != None:
                p_avatar = request.data['profile_photo']
                result = urllib2.urlretrieve(p_avatar)
                player.profile_photo.save(
                    os.path.basename(
                        player.first_name + '-' + player.last_name + '.png'),
                    File(open(result[0], 'rb'))
                )
            else:
                player.profile_photo = None
        else:
            if p_avatar != None:
                p_avatar = request.data['profile_photo']
                result = urllib2.urlretrieve(p_avatar)
                player.profile_photo.save(
                    os.path.basename(p_avatar),
                    File(open(result[0], 'rb'))
                )
            else:
                player.profile_photo = None
        firstname = request.data['first_name']
        if firstname != None and firstname != '':
            player.firstname = firstname.title()
        lastname = request.data['last_name']
        if lastname != None and lastname != '':
            player.last_name = lastname.title()
        fullname = firstname + ' ' + lastname
        p_height = request.data['height']
        p_weight = request.data['weight']
        p_city = request.data['city']
        p_vertical = request.data['vertical']
        p_fourty_yard_dash = request.data['fourty_yard_dash']
        p_short_shuttle = request.data['short_shuttle']

        if p_city != None and p_city != '':
            player_city = p_city['name']
        else:
            player_city = None
        p_state = request.data['state']
        if p_state != None and p_state != '':
            player_state = p_state['name']
        else:
            player_state = None
        p_school = request.data['school']
        if p_school != None and p_school != '':
            player_school = p_school['name']
        else:
            player_school = None

        p_class = request.data['classification']
        if p_class != None and p_class != '':
            player_class = p_class['year']
        else:
            player_class = None
        p_positions = request.data['position']
        p_avg_transition_time = request.data['avg_transition_time']
        p_avg_closing_speed = request.data['avg_closing_speed']
        p_avg_yards_of_seperation = request.data['avg_yards_of_seperation']
        p_top_speed = request.data['top_speed']
        p_time_to_top_speed = request.data['time_to_top_speed']
        p_sack = request.data['sack']
        p_interception = request.data['interception']
        p_touchdown = request.data['touchdown']

        # FBS Offers
        # p_fbs_offer = request.data['fbs_offers']
        # if p_fbs_offer:
        #     p_decommit = p_fbs_offer['decommit']
        #     # Decommit
        #     if p_decommit:
        #         p_decommit_date = p_decommit['decommited_on']
        #         if p_decommit_date:
        #             decommit_date = p_decommit_date
        #         else:
        #             decommit_date = None
        #         p_decommit_school = p_decommit['school']
        #         if p_decommit_school:
        #             decommit_school = p_decommit_school['name']
        #     else:
        #         decommit_date = None
        #         decommit_school = None

        #     # Hard Commit
        #     p_commit = p_fbs_offer['hard_commit']
        #     if p_commit:
        #         p_commit_date = p_commit['commited_on']
        #         if p_commit_date:
        #             commit_date = p_commit_date
        #         else:
        #             commit_date = None
        #         p_commit_school = p_commit['school']
        #         if p_commit_school:
        #             commit_school = p_commit_school['name']
        #     else:
        #         commit_date = None
        #         commit_school = None

        #     # Visits
        #     p_visits = p_fbs_offer['visits']
        #     if p_visits:
        #         school_visits = []
        #         for school_nm in p_visits['schools']:
        #             nm = school_visits.append(school_nm)
        #     else:
        #         school_visits = []
        #     if p_fbs_offer:
        #         fbs_schools = []
        #         p_fbs_schools = p_fbs_offer['schools']
        #         for school_nm in p_fbs_schools:
        #             nm = fbs_schools.append(school_nm)
        #     else:
        #         fbs_schools = []

        if p_height != None and p_height != '':
            if len(p_height) == 1:
                feet = int(p_height)
                inches = 0
                player_height = (feet*12 + inches)
                player.height = player_height
            else:
                if len(p_height) >= 3:
                    list_obj = p_height.split('.')
                    feet = int(list_obj[0])
                if len(list_obj) >= 2:
                    inches = int(list_obj[1])
                else:
                    inches = 0
                player_height = (feet*12 + inches)
                player.height = player_height
        else:
            player.height = None

        if p_weight != None and p_weight != '':
            player.weight = p_weight
        else:
            player.weight = None

        if p_avg_transition_time != None and p_avg_transition_time != '':
            player.avg_transition_time = p_avg_transition_time
        else:
            player.avg_transition_time = None

        if p_avg_closing_speed != None and p_avg_closing_speed != '':
            player.avg_closing_speed = p_avg_closing_speed
        else:
            player.avg_closing_speed = None

        if p_avg_yards_of_seperation != None and p_avg_yards_of_seperation != '':
            player.avg_yards_of_seperation = p_avg_yards_of_seperation
        else:
            player.avg_yards_of_seperation = None

        if p_top_speed != None and p_top_speed != '':
            player.top_speed = p_top_speed
        else:
            player.top_speed = None

        if p_time_to_top_speed != None and p_time_to_top_speed != '':
            player.time_to_top_speed = p_time_to_top_speed
        else:
            player.time_to_top_speed = None

        if p_sack != None and p_sack != '':
            player.sack = p_sack
        else:
            player.sack = None

        if p_interception != None and p_interception != '':
            player.interception = p_interception
        else:
            player.interception = None
        # playmaking_analyze = []
        # playmaking_analyze.append(p_interception)
        # playmaking_analyze.append(p_sack)
        # playmaking_analyze.append(p_touchdown)
        # playmaking_score = get_playmaking(player, playmaking_analyze)

        if p_touchdown != None and p_touchdown != '':
            player.touchdown = p_touchdown
        else:
            player.touchdown = None

        if player_city != None and player_city != '':
            p_city = City.objects.filter(name__iexact=player_city)
            if p_city:
                player.city = p_city[0]
        else:
            player.city = None

        if player_state != None and player_state != '':
            p_state = State.objects.get(name__iexact=player_state)
            player.state = p_state
        else:
            player.state = None

        if player_class != None and player_class != '':
            try:
                p_class = Classification.objects.get(
                    year__iexact=player_class)
                player.classification = p_class
            except Classification.DoesNotExist:
                p_class = Classification.objects.create(
                    year=player_class)
                player.classification = p_class
        else:
            player.classification = None
        p_social_engagement = request.data['social_engagement']
        if p_social_engagement != None and p_social_engagement != '':
            if p_social_engagement['twitter_handle'] != None and \
                    p_social_engagement['twitter_handle'] != '':
                plyr_twitter_handle = p_social_engagement['twitter_handle']
            else:
                plyr_twitter_handle = None
            if p_social_engagement['followers'] != None and p_social_engagement['followers'] != '':
                plyr_twitter_followers = p_social_engagement['followers']
            else:
                plyr_twitter_followers = None
            if p_social_engagement['following'] != None and p_social_engagement['following'] != '':
                plyr_twitter_following = p_social_engagement['following']
            else:
                plyr_twitter_following = None
            if p_social_engagement['tweets'] != None and p_social_engagement['tweets'] != '':
                plyr_twitter_tweets = p_social_engagement['tweets']
            else:
                plyr_twitter_tweets = None
            if p_social_engagement['key_people_followers'] != None and \
                    p_social_engagement['key_people_followers'] != '':
                plyr_twitter_key_ppl_followers = p_social_engagement['key_people_followers']
            else:
                plyr_twitter_key_ppl_followers = None
            if p_social_engagement['key_people_followings'] != None and \
                    p_social_engagement['key_people_followings'] != '':
                plyr_twitter_key_ppl_following = p_social_engagement['key_people_followings']
            else:
                plyr_twitter_key_ppl_following = None
            if p_social_engagement['retweets'] != None and \
                    p_social_engagement['retweets'] != '':
                plyr_twitter_retweets = p_social_engagement['retweets']
            else:
                plyr_twitter_retweets = None
            if p_social_engagement['new_followers'] != None and \
                    p_social_engagement['new_followers'] != '':
                plyr_twitter_new_followers = p_social_engagement['new_followers']
            else:
                plyr_twitter_new_followers = None
            if p_social_engagement['newly_followed'] != None and \
                    p_social_engagement['newly_followed'] != '':
                plyr_twitter_newly_followed = p_social_engagement['newly_followed']
            else:
                plyr_twitter_newly_followed = None
        else:
            player_social = None

        if p_social_engagement != None:
            p_twitter = SocialEngagement.objects.create(
                twitter_handle=plyr_twitter_handle,
                followers=plyr_twitter_followers,
                following=plyr_twitter_following,
                tweets=plyr_twitter_tweets,
                retweets=plyr_twitter_retweets,
                key_people_followers=plyr_twitter_key_ppl_followers,
                key_people_followings=plyr_twitter_key_ppl_following,
                new_followers=plyr_twitter_new_followers,
                newly_followed=plyr_twitter_newly_followed
            )
            player.social_engagement = p_twitter
        else:
            player.social_engagement = None
        # Personality Insights
        p_pers_insights = request.data['personality_insight']
        if p_pers_insights != None and p_pers_insights != '':
            p_pers_insights_personality = p_pers_insights['personality']
            if p_pers_insights_personality != None:
                personality_cochability = p_pers_insights_personality['coachability']
                if personality_cochability:
                    p_personality_cochability = personality_cochability
                else:
                    p_personality_cochability = None
                personality_extroverted = p_pers_insights_personality['extroverted']
                if personality_extroverted:
                    p_personality_extroverted = personality_extroverted
                else:
                    p_personality_extroverted = None
                personality_openness = p_pers_insights_personality['openness']
                if personality_openness:
                    p_personality_openness = personality_openness
                else:
                    p_personality_openness = None
                personality_team_player = p_pers_insights_personality['team_player']
                if personality_team_player:
                    p_personality_team_player = personality_team_player
                else:
                    p_personality_team_player = None
                personality_temperament = p_pers_insights_personality['temperament']
                if personality_temperament:
                    p_personality_temperament = personality_temperament
                else:
                    p_personality_temperament = None
            p_pers_insights_values = p_pers_insights['values']
            if p_pers_insights_values != None:
                values_achievement = p_pers_insights_values['achievement']
                if values_achievement:
                    p_values_achievement = values_achievement
                else:
                    p_values_achievement = None
                values_helping_others = p_pers_insights_values['helping_others']
                if values_helping_others:
                    p_values_helping_others = values_helping_others
                else:
                    p_values_helping_others = None
                values_stimulation = p_pers_insights_values['stimulation']
                if values_stimulation:
                    p_values_stimulation = values_stimulation
                else:
                    p_values_stimulation = None
                values_takin_pleasure_life = p_pers_insights_values['taking_pleasure_in_life']
                if values_takin_pleasure_life:
                    p_values_takin_pleasure_life = values_takin_pleasure_life
                else:
                    p_values_takin_pleasure_life = None
                values_tradition = p_pers_insights_values['tradition']
                if values_tradition:
                    p_values_tradition = values_tradition
                else:
                    p_values_tradition = None
            p_pers_insights_needs = p_pers_insights['needs']
            if p_pers_insights_needs != None:
                needs_challenge = p_pers_insights_needs['challenge']
                if needs_challenge:
                    p_needs_challenge = needs_challenge
                else:
                    p_needs_challenge = None
                needs_excitement = p_pers_insights_needs['excitement']
                if needs_excitement:
                    p_needs_excitement = needs_excitement
                else:
                    p_needs_excitement = None
                needs_ideal = p_pers_insights_needs['ideal']
                if needs_ideal:
                    p_needs_ideal = needs_ideal
                else:
                    p_needs_ideal = None
                needs_stability = p_pers_insights_needs['stability']
                if needs_stability:
                    p_needs_stability = needs_stability
                else:
                    p_needs_stability = None
                needs_structure = p_pers_insights_needs['structure']
                if needs_structure:
                    p_needs_structure = needs_structure
                else:
                    p_needs_structure = None

                if p_pers_insights_needs != None:
                    pi_needs = ProspectsNeeds.objects.create(
                        challenge=p_needs_challenge,
                        structure=p_needs_structure,
                        stability=p_needs_stability,
                        excitement=p_needs_excitement,
                        ideal=p_needs_ideal,
                    )
                if p_pers_insights_values != None:
                    pi_values = ProspectsValues.objects.create(
                        tradition=p_values_tradition,
                        stimulation=p_values_stimulation,
                        helping_others=p_values_helping_others,
                        achievement=p_values_achievement,
                        taking_pleasure_in_life=p_values_takin_pleasure_life,
                    )
                if p_pers_insights_personality != None:
                    pi_personality = ProspectsPersonality.objects.create(
                        team_player=p_personality_team_player,
                        coachability=p_personality_cochability,
                        openness=p_personality_openness,
                        extroverted=p_personality_extroverted,
                        temperament=p_personality_temperament,
                    )
                player_pi = PersonalityInsights.objects.create(
                    personality=pi_personality,
                    values=pi_values,
                    needs=pi_needs,
                )
                player.personality_insight = player_pi
            else:
                player.personality_insight = None

            if player_city != None:
                city_obj = City.objects.filter(name__iexact=player_city)
                if city_obj:
                    player.city = city_obj[0]
            else:
                player.city = None

            if player_state != None:
                state_obj = State.objects.get(
                    name__iexact=player_state)
                player.state = state_obj
            else:
                player.state = None

            if p_positions:
                if len(p_positions) >= 1:
                    player.position.clear()
                    for pos in p_positions:
                        try:
                            pos_obj = Positions.objects.get(
                                name__iexact=pos)
                            player.position.add(pos_obj)
                        except Exception as e:
                            print(e)

            if player_school != None:
                school_obj = School.objects.get(
                    name__iexact=player_school)
                player.school = school_obj
            else:
                player.school = None

            if p_vertical:
                player.vertical = p_vertical
            else:
                player.vertical = None

            if p_short_shuttle:
                player.short_shuttle = p_short_shuttle
            else:
                player.short_shuttle = None

            if p_fourty_yard_dash:
                player.fourty_yard_dash = p_fourty_yard_dash
            else:
                player.fourty_yard_dash = None
            playmaking_analyze = []
            playmaking_analyze.append(p_interception)
            playmaking_analyze.append(p_sack)
            playmaking_analyze.append(p_touchdown)
            playmaking_score = get_playmaking(player, playmaking_analyze)
            athleticism_analyze = {}
            athleticism_analyze['avg_yards_of_seperation'] = p_avg_yards_of_seperation
            athleticism_analyze['avg_closing_speed'] = p_avg_closing_speed
            athleticism_analyze['top_speed'] = p_top_speed
            athleticism_analyze['avg_transition_time'] = p_avg_transition_time
            athleticism_analyze['time_to_top_speed'] = p_time_to_top_speed
            athleticism_sco = get_athleticism(player, athleticism_analyze)
            # player.save()
            if player.play_making is None and player.athleticism is None:
                player.film_grade = None
                player_role = PlayerType.objects.get(
                    name__iexact='prospect')
                player.role = player_role
            else:
                if (player.athleticism is not None) and (player.play_making is not None):
                    film_grade = (player.athleticism +
                                  player.play_making) / 2
                    player.film_grade = film_grade
                elif (player.athleticism is not None) and (player.play_making is None):
                    film_grade = (player.athleticism + 0) / 2
                    player.film_grade = film_grade
                elif (player.athleticism is None) and (player.play_making is not None):
                    film_grade = (0 + player.play_making) / 2
                    player.film_grade = film_grade
                else:
                    player.film_grade = None

        priority_counts = Player.objects.all().exclude(
            role__name__iexact='nfl').order_by(F('priority').desc(nulls_last=True))
        next_priority_no = priority_counts[0].priority + 1
        player.priority = next_priority_no
        player.save()

        try:
            OldPlayMakingValues.objects.create(
                                player=player,
                                old_interception_maxpreps=player.interception,
                                old_sack_maxpreps=player.sack,
                                old_touchdown_maxpreps=player.touchdown
                                )
        except Exception as e:
            print(e)

    # PUT Call Started
    if request.method == 'PUT':
        if 'id' in request.data:
            try:
                player = Player.objects.get(id=request.data['id'])
                p_avatar = request.data['profile_photo']
                if player.profile_photo:
                    if p_avatar != None:
                        p_avatar = request.data['profile_photo']
                        result = urllib2.urlretrieve(p_avatar)
                        player.profile_photo.save(
                            os.path.basename(
                                player.first_name + '-' + player.last_name + '.png'),
                            File(open(result[0], 'rb'))
                        )
                    else:
                        player.profile_photo = None
                else:
                    if p_avatar != None:
                        p_avatar = request.data['profile_photo']
                        result = urllib2.urlretrieve(p_avatar)
                        player.profile_photo.save(
                            os.path.basename(p_avatar),
                            File(open(result[0], 'rb'))
                        )
                    else:
                        player.profile_photo = None

                firstname = request.data['first_name']
                if firstname != None and firstname != '':
                    player.first_name = firstname.title()
                lastname = request.data['last_name']
                if lastname != None and lastname != '':
                    player.last_name = lastname.title()
                fullname = firstname + ' ' + lastname
                p_height = request.data['height']
                p_weight = request.data['weight']
                p_city = request.data['city']
                p_vertical = request.data['vertical']
                p_fourty_yard_dash = request.data['fourty_yard_dash']
                p_short_shuttle = request.data['short_shuttle']
                if 'video_highlight' in request.data:
                    #player.video_highlight = request.data['video_highlight']
                    url = request.data['video_highlight']
                    if url != '' and url != None:
                        get_highlighted_video(player,url)
                    else:
                        player.web_highlighted_video = None
                        player.video_highlight = None
                        player.save()
                else:
                    player.video_highlight = None
                if p_city != None and p_city != '':
                    player_city = p_city['name']
                else:
                    player_city = None
                p_state = request.data['state']
                if p_state != None and p_state != '':
                    player_state = p_state['name']
                else:
                    player_state = None
                p_school = request.data['school']
                if p_school != None and p_school != '':
                    player_school = p_school['name']
                else:
                    player_school = None

                p_class = request.data['classification']
                if p_class != None and p_class != '':
                    player_class = p_class['year']
                else:
                    player_class = None
                p_positions = request.data['position']
                p_avg_transition_time = request.data['avg_transition_time']
                p_avg_closing_speed = request.data['avg_closing_speed']
                p_avg_yards_of_seperation = request.data['avg_yards_of_seperation']
                p_top_speed = request.data['top_speed']
                p_time_to_top_speed = request.data['time_to_top_speed']
                p_sack = request.data['sack']
                p_interception = request.data['interception']
                p_touchdown = request.data['touchdown']
                # FBS Offers
                p_fbs_offer = request.data['fbs_offers']
                if p_fbs_offer:
                    p_decommit = p_fbs_offer['decommit']
                    # Decommit
                    if p_decommit:
                        p_decommit_date = p_decommit['decommited_on']
                        if p_decommit_date:
                            decommit_date = p_decommit_date
                        else:
                            decommit_date = None
                        p_decommit_school = p_decommit['school']
                        if p_decommit_school:
                            decommit_school = p_decommit_school['name']
                        else:
                            decommit_school = None
                    else:
                        decommit_date = None
                        decommit_school = None

                    # Hard Commit
                    p_commit = p_fbs_offer['hard_commit']
                    if p_commit:
                        p_commit_date = p_commit['commited_on']
                        if p_commit_date:
                            commit_date = p_commit_date
                        else:
                            commit_date = None
                        p_commit_school = p_commit['school']
                        if p_commit_school:
                            commit_school = p_commit_school['name']
                        else:
                            commit_school = None
                    else:
                        commit_date = None
                        commit_school = None

                    # Visits
                    p_visits = p_fbs_offer['visits']
                    if p_visits:
                        school_visits = []
                        for school_nm in p_visits['schools']:
                            nm = school_visits.append(school_nm)
                    else:
                        school_visits = []
                    if p_fbs_offer:
                        fbs_schools = []
                        p_fbs_schools = p_fbs_offer['schools']
                        for school_nm in p_fbs_schools:
                            nm = fbs_schools.append(school_nm)
                    else:
                        fbs_schools = []
                else:
                    p_commit = None
                    p_decommit = None
                    p_visits = None
                    p_fbs_schools = None
                    school_visits = []
                    fbs_schools = []

                # Fbs Offers

                if firstname != None and firstname != '':
                    player.first_name = firstname
                else:
                    player.first_name = None
                if lastname != None and lastname != '':
                    player.last_name = lastname
                player.full_name = firstname + ' ' + lastname
                if player.height:
                    if p_height != None and p_height != '':
                        if len(p_height) == 1:
                            feet = int(p_height)
                            inches = 0
                            player_height = (feet*12 + inches)
                            player.height = player_height
                        else:
                            if len(p_height) >= 3:
                                list_obj = p_height.split('.')
                                feet = int(list_obj[0])
                            if len(list_obj) >= 2:
                                inches = int(list_obj[1])
                            else:
                                inches = 0
                            player_height = (feet*12 + inches)
                            player.height = player_height
                    else:
                        player.height = None
                else:
                    if p_height != None and p_height != '':
                        if len(p_height) == 1:
                            feet = int(p_height)
                            inches = 0
                            player_height = (feet*12 + inches)
                            player.height = player_height
                        else:
                            if len(p_height) >= 3:
                                list_obj = p_height.split('.')
                                feet = int(list_obj[0])
                            if len(list_obj) >= 2:
                                inches = int(list_obj[1])
                            else:
                                inches = 0
                            player_height = (feet*12 + inches)
                            player.height = player_height
                    else:
                        player.height = None

                if player.weight:
                    if p_weight != None and p_weight != '':
                        player.weight = p_weight
                    else:
                        player.weight = None
                else:
                    if p_weight != None:
                        player.weight = p_weight
                    else:
                        player.weight = None
                if player.avg_transition_time:
                    if p_avg_transition_time != None and p_avg_transition_time != '':
                        player.avg_transition_time = p_avg_transition_time
                    else:
                        player.avg_transition_time = None
                else:
                    if p_avg_transition_time != None and p_avg_transition_time != '':
                        player.avg_transition_time = p_avg_transition_time
                    else:
                        player.avg_transition_time = None
                if player.avg_closing_speed:
                    if p_avg_closing_speed != None and p_avg_closing_speed != '':
                        player.avg_closing_speed = p_avg_closing_speed
                    else:
                        player.avg_closing_speed = None
                else:
                    if p_avg_closing_speed != None and p_avg_closing_speed != '':
                        player.avg_closing_speed = p_avg_closing_speed
                    else:
                        player.avg_closing_speed = None
                if player.avg_yards_of_seperation:
                    if p_avg_yards_of_seperation != None and p_avg_yards_of_seperation != '':
                        player.avg_yards_of_seperation = p_avg_yards_of_seperation
                    else:
                        player.avg_yards_of_seperation = None
                else:
                    if p_avg_yards_of_seperation != None and p_avg_yards_of_seperation != '':
                        player.avg_yards_of_seperation = p_avg_yards_of_seperation
                    else:
                        player.avg_yards_of_seperation = None
                if player.top_speed:
                    if p_top_speed != None and p_top_speed != '':
                        player.top_speed = p_top_speed
                    else:
                        player.top_speed = None
                else:
                    if p_top_speed != None and p_top_speed != '':
                        player.top_speed = p_top_speed
                    else:
                        player.top_speed = None
                if player.time_to_top_speed:
                    if p_time_to_top_speed != None and p_time_to_top_speed != '':
                        player.time_to_top_speed = p_time_to_top_speed
                    else:
                        player.time_to_top_speed = None
                else:
                    if p_time_to_top_speed != None and p_time_to_top_speed != '':
                        player.time_to_top_speed = p_time_to_top_speed
                    else:
                        player.time_to_top_speed = None
                if player.sack:
                    if p_sack != None and p_sack != '':
                        player.sack = p_sack
                    else:
                        player.sack = None
                else:
                    if p_sack != None and p_sack != '':
                        player.sack = p_sack
                    else:
                        player.sack = None
                if player.interception:
                    if p_interception != None and p_interception != '':
                        player.interception = p_interception
                    else:
                        player.interception = None
                else:
                    if p_interception != None and p_interception != '':
                        player.interception = p_interception
                    else:
                        player.interception = None
                if player.touchdown:
                    if p_touchdown != None and p_touchdown != '':
                        player.touchdown = p_touchdown
                    else:
                        player.touchdown = None
                else:
                    if p_touchdown != None and p_touchdown != '':
                        player.touchdown = p_touchdown
                    else:
                        player.touchdown = None
                notifications_total_offer_checker = ''
                notification_schools_offer_checker = ''
                notification_hard_commit_school = ''
                notification_hard_commit_date = ''
                notification_decommit_school = ''
                notification_decommit_date = ''
                add_count = []
                if player.fbs_offers:
                    # if len(fbs_schools) == 0:
                    #     if player.fbs_offers.total != None:
                    #         notifications_total_offer_checker = 'raised'
                    # if commit_date == None and commit_school == None:
                    #     if player.fbs_offers.hard_commit != None and\
                    #          player.fbs_offers.hard_commit.school != None and\
                    #               player.fbs_offers.hard_commit.school.name != None:
                    #         print("notify.....!!!!!")
                    #         notification_hard_commit_date = 'raised'
                    # if decommit_date == None and decommit_school == None:
                    #     if player.fbs_offers.decommit != None and player.fbs_offers.decommit.school != None and player.fbs_offers.decommit.school.name != None:
                    #         notification_decommit_date = 'raised'

                    fbs_obj = FbsOffers.objects.get(id=player.fbs_offers.id)
                    add_count = []
                    if len(fbs_schools) > 0:
                        try:
                            if len(player.fbs_offers.schools.all()) != ('' or None or 0):
                                existing_offer_total = len(
                                    player.fbs_offers.schools.all())
                                put_offer_total = len(fbs_schools)
                                if put_offer_total != existing_offer_total:
                                    existing_schools = list(
                                        player.fbs_offers.schools.all().values_list('name', flat=True))
                                    for fbs_school in existing_schools:
                                        if fbs_school not in fbs_schools:
                                            school_ob = School.objects.get(
                                                name__iexact=fbs_school)
                                            delete_fbs_sch = FbsSchools.objects.filter(
                                                fbs_offer=fbs_obj,
                                                school=school_ob
                                            ).delete()
                                            notification_schools_offer_checker = 'raised'
                                    for new_fbs in fbs_schools:
                                        updated_existing_schools = list(
                                            player.fbs_offers.schools.all().values_list('name', flat=True))
                                        if new_fbs not in updated_existing_schools:
                                            new_school_obj = School.objects.get(
                                                name__iexact=new_fbs)
                                            adding_fbs_sch = FbsSchools.objects.create(
                                                fbs_offer=fbs_obj,
                                                school=new_school_obj,
                                                status='new'
                                            )
                                            notifications_total_offer_checker = 'raised'
                                            add_count.append('added')
                                    fbs_obj.total = str(put_offer_total)
                                    fbs_obj.save()
                                # if existing_offer_total != put_offer_total:
                                # elif put_offer_total > existing_offer_total:
                                #     #updated_count = int(put_offer_total) - int(existing_offer_total)
                                #     if updated_count != '':
                                #         for sch in fbs_schools:
                                #             try:
                                #                 fbs_school_obj = School.objects.get(name__iexact=sch.strip())
                                #                 try:
                                #                     fbs_school_obj = FbsSchools.objects.get(
                                #                         fbs_offer=player.fbs_offers,
                                #                         school=fbs_school_obj,
                                #                         status='new'
                                #                     )
                                #                     #fbs_school_obj.save()
                                #                 except FbsSchools.DoesNotExist:
                                #                     fbs_school_obj = FbsSchools.objects.create(
                                #                         fbs_offer=player.fbs_offers,
                                #                         school=fbs_school_obj,
                                #                         status='new'
                                #                     )
                                #                     #fbs_school_obj.save()
                                #             except Exception as e:
                                #                 print(e)
                                #         fbs_obj.total = str(len(fbs_schools))
                                #         fbs_obj.save()
                                    # player.fbs_offers = fbs_obj
                                    #updated_count = int(existing_offer_total) + int(put_offer_total)
                                    #updated_count - int(existing_offer_total)
                                    #notifications_count = updated_count
                                else:
                                    if put_offer_total == existing_offer_total:
                                        existing_schools = list(
                                            player.fbs_offers.schools.all().values_list('name', flat=True))
                                        for fbs_school in existing_schools:
                                            if fbs_school not in fbs_schools:
                                                school_ob = School.objects.filter(
                                                    name__iexact=fbs_school)[0]
                                                delete_fbs_sch = FbsSchools.objects.filter(
                                                    fbs_offer=fbs_obj,
                                                    school=school_ob
                                                ).delete()
                                                notification_schools_offer_checker = 'raised'
                                        for new_fbs in fbs_schools:
                                            updated_existing_schools = list(
                                                player.fbs_offers.schools.all().values_list('name', flat=True))
                                            if new_fbs not in updated_existing_schools:
                                                new_school_obj = School.objects.filter(
                                                    name__iexact=new_fbs)[0]
                                                adding_fbs_sch = FbsSchools.objects.create(
                                                    fbs_offer=fbs_obj,
                                                    school=new_school_obj,
                                                    status='new'
                                                )
                                                notification_schools_offer_checker = 'raised'
                                                add_count.append('added')
                                        fbs_obj.total = str(put_offer_total)
                                        fbs_obj.save()
                                # fbs_obj.total = len(fbs_schools)
                                # fbs_obj.save()
                            else:
                                fbs_obj = FbsOffers.objects.get(
                                    id=player.fbs_offers.id)
                                for new_fbs in fbs_schools:
                                    new_school_obj = School.objects.filter(
                                        name__iexact=new_fbs)[0]
                                    adding_fbs_sch = FbsSchools.objects.create(
                                        fbs_offer=fbs_obj,
                                        school=new_school_obj,
                                        status='new'
                                    )
                                    notifications_total_offer_checker = 'raised'
                                    add_count.append('added')
                                total_count = len(
                                    player.fbs_offers.schools.all())
                                fbs_obj.total = str(total_count)
                                fbs_obj.save()

                        except Exception as e:
                            print(e)
                    else:
                        if player.fbs_offers:
                            fbs_obj = FbsOffers.objects.get(
                                id=player.fbs_offers.id)
                            existing_schools = list(
                                player.fbs_offers.schools.all().values_list('name', flat=True))
                            for fbs_school in existing_schools:
                                try:
                                    school_ob = School.objects.get(
                                        name__iexact=fbs_school)
                                    delete_fbs_sch = FbsSchools.objects.filter(
                                        fbs_offer=fbs_obj,
                                        school=school_ob
                                    ).delete()
                                except Exception as e:
                                    print(e)
                                notification_schools_offer_checker = 'raised'
                            fbs_obj.total = None
                            fbs_obj.save()


                    if player.fbs_offers.visits != None:
                        visit_schools_objs = School.objects.filter(
                            name__in=school_visits)
                        visit_obj = SchoolsVisit.objects.get(
                            id=player.fbs_offers.visits.id)
                        visit_obj.schools.clear()
                        visit_obj.total = None
                        visit_obj.save()
                        if len(visit_schools_objs) >= 1:
                            for school_obj in visit_schools_objs:
                                visit_obj.schools.add(school_obj.id)

                            visit_obj.total = len(visit_schools_objs)
                            fbs_obj.visits = visit_obj
                            fbs_obj.save()
                            player.fbs_offers = fbs_obj
                        else:
                            visit_obj.total = None
                            fbs_obj.visits = visit_obj
                            fbs_obj.save()
                            player.fbs_offers = fbs_obj
                    else:
                        if len(school_visits) >= 1:
                            visit_obj = SchoolsVisit.objects.create(
                                total=len(school_visits))
                            visit_schools_objs = School.objects.filter(
                                name__in=school_visits)
                            for school_obj in visit_schools_objs:
                                visit_obj.schools.add(school_obj.id)
                            fbs_obj.visits = visit_obj
                            fbs_obj.save()

                    if commit_date != None and commit_school != None:
                        if player.fbs_offers.hard_commit != None:
                            hard_commit_obj = FbsHardCommit.objects.get(
                                id=player.fbs_offers.hard_commit.id)
                            if commit_school != None:
                                try:
                                    hard_commit_school_obj = School.objects.get(
                                        name__iexact=commit_school)
                                except Exception as e:
                                    hard_commit_school_obj = School.objects.create(
                                        name=commit_school)
                                if hard_commit_obj.school == None:
                                    notification_hard_commit_school = 'raised'
                                if hard_commit_obj.school != None:
                                    if hard_commit_obj.school.name.lower().strip() == hard_commit_school_obj.name.lower().strip():
                                        notification_hard_commit_school = 'unraised'
                                    else:
                                        notification_hard_commit_school = 'raised'

                                hard_commit_sch = None
                                try:
                                    hard_commit_sch = School.objects.get(
                                        name__iexact=commit_school)
                                except School.DoesNotExist:
                                    hard_commit_sch = School.objects.create(
                                        name=commit_school)
                                if hard_commit_sch != None:
                                    hard_commit_obj.school = hard_commit_sch
                                    # hard_commit_obj = FbsHardCommit.objects.create(
                                    #     school=hard_commit_sch)
                                    if commit_date != None:
                                        hard_commit_obj.commited_on = commit_date
                                        hard_commit_obj.save()
                                        fbs_obj.hard_commit = hard_commit_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                            else:
                                hard_commit_obj.school = None
                                hard_commit_obj.commited_on = None
                                hard_commit_obj.save()
                                fbs_obj.hard_commit = hard_commit_obj
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj
                        else:
                            hard_commit_obj = None
                            if commit_school != None and commit_school != '':
                                try:
                                    hard_commit_sch = School.objects.filter(
                                        name__iexact=commit_school
                                    )[0]
                                except School.DoesNotExist:
                                    hard_commit_sch = School.objects.create(
                                        name=commit_school
                                    )
                                if hard_commit_sch != None:
                                    hard_commit_obj = FbsHardCommit.objects.create(
                                        school=hard_commit_sch
                                    )
                                    if commit_date != None:
                                        hard_commit_obj.commited_on = commit_date
                                        hard_commit_obj.save()
                                        fbs_obj.hard_commit = hard_commit_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                        notification_hard_commit_date = 'raised'
                                        notification_hard_commit_school = 'raised'
                    else:
                        if player.fbs_offers.hard_commit != None:
                            hard_commit_obj = FbsHardCommit.objects.get(
                                id=player.fbs_offers.hard_commit.id
                            )
                            if player.fbs_offers.hard_commit.school != None:
                                notification_hard_commit_school = 'raised'
                            hard_commit_obj.school = None
                            hard_commit_obj.commited_on = None
                            hard_commit_obj.save()
                            fbs_obj.hard_commit = hard_commit_obj
                            fbs_obj.save()
                            player.fbs_offers = fbs_obj
                    if decommit_date != None and decommit_school != None:
                        if player.fbs_offers.decommit != None:
                            decommit_obj = FbsDeCommit.objects.get(
                                id=player.fbs_offers.decommit.id)
                            fbs_obj = FbsOffers.objects.get(
                                id=player.fbs_offers.id)
                            if decommit_school:
                                try:
                                    decommit_sch = School.objects.filter(
                                        name__iexact=decommit_school
                                    )[0]
                                except School.DoesNotExist:
                                    decommit_sch = School.objects.create(
                                        name=decommit_school
                                    )
                                if player.fbs_offers.decommit.school == None:
                                    notification_decommit_school = 'raised'
                                if decommit_obj.school != None:
                                    if decommit_obj.school.name.lower().strip() == decommit_sch.name.lower().strip():
                                        notification_decommit_school = 'unraised'
                                    else:
                                        notification_decommit_school = 'raised'

                                decommit_obj.school = decommit_sch
                                decommit_obj.decommited_on = decommit_date
                                decommit_obj.save()
                                fbs_obj.decommit = decommit_obj
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj
                            else:
                                decommit_obj.school = None
                                decommit_obj.decommited_on = None
                                decommit_obj.save()
                                fbs_obj.decommit = decommit_obj
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj

                        else:
                            decommit_obj = None
                            if decommit_school != None and decommit_school != '':
                                try:
                                    decommit_sch = School.objects.get(
                                        name__iexact=decommit_school)
                                except School.DoesNotExist:
                                    decommit_sch = School.objects.create(
                                        name=decommit_school)
                                if decommit_sch != None:
                                    decommit_obj = FbsDeCommit.objects.create(
                                        school=decommit_sch)
                                    if decommit_date != None:
                                        decommit_obj.decommited_on = decommit_date
                                        decommit_obj.save()
                                        fbs_obj.decommit = decommit_obj
                                        fbs_obj.save()
                                        player.fbs_offers = fbs_obj
                                        notification_decommit_date = 'raised'
                    else:
                        if player.fbs_offers.decommit != None:
                            decommit_obj = FbsDeCommit.objects.get(
                                id=player.fbs_offers.decommit.id
                            )
                            if player.fbs_offers.decommit.school != None:
                                notification_decommit_school = 'raised'
                            decommit_obj.school = None
                            decommit_obj.decommited_on = None
                            decommit_obj.save()
                            fbs_obj.decommit = decommit_obj
                            fbs_obj.save()
                            player.fbs_offers = fbs_obj

                else:
                    fbs_obj = None
                    hard_commit_obj = None
                    decommit_obj = None
                    visits_obj = None
                    if len(fbs_schools) >= 1:
                        fbs_obj = FbsOffers.objects.create(
                            total=str(len(fbs_schools))
                        )
                        fbs_schools_objs = School.objects.filter(
                            name__in=fbs_schools)
                        for school_obj in fbs_schools_objs:
                            try:
                                fbs_school_obj = FbsSchools.objects.get(
                                    fbs_offer=fbs_obj,
                                    school=school_obj,
                                    status='new'
                                )
                                # fbs_school_obj.save()
                            except FbsSchools.DoesNotExist:
                                fbs_school_obj = FbsSchools.objects.create(
                                    fbs_offer=fbs_obj,
                                    school=school_obj,
                                    status='new'
                                )
                        #fbs_obj.total = str(len(fbs_schools))
                        fbs_obj.save()
                        player.fbs_offers = fbs_obj
                        #notifications_count = len(fbs_schools)
                        for fbs_s in fbs_schools:
                            add_count.append(fbs_s)
                        notifications_total_offer_checker = 'raised'
                    if p_commit != None:
                        hard_commit_sch = None
                        try:
                            if commit_school != None:
                                hard_commit_sch = School.objects.get(
                                    name__iexact=commit_school)
                        except School.DoesNotExist:
                            if commit_school != None:
                                hard_commit_sch = School.objects.create(
                                    name=commit_school)
                        # if commit_school != None:
                        if hard_commit_sch != None:
                            hard_commit_obj = FbsHardCommit.objects.create(
                                school=hard_commit_sch)
                            if commit_date != None:
                                hard_commit_obj.commited_on = commit_date
                                hard_commit_obj.save()
                                if fbs_obj != None:
                                    fbs_obj.hard_commit = hard_commit_obj
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                                else:
                                    fbs_obj = FbsOffers.objects.create(
                                        hard_commit=hard_commit_obj)
                                    player.fbs_offers = fbs_obj
                                notification_hard_commit_school = 'raised'
                        else:
                            if fbs_obj != None:
                                fbs_obj.hard_commit = None
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj

                    if p_decommit != None:
                        decommit_sch = None
                        try:
                            if decommit_school != None:
                                decommit_sch = School.objects.get(
                                    name__iexact=decommit_school)
                        except School.DoesNotExist:
                            if decommit_school != None:
                                decommit_sch = School.objects.create(
                                    name=decommit_school)
                        # if commit_school != None:
                        if decommit_sch != None:
                            decommit_obj = FbsDeCommit.objects.create(
                                school=decommit_sch)
                            if decommit_date != None:
                                decommit_obj.decommited_on = decommit_date
                                decommit_obj.save()
                                if fbs_obj != None:
                                    fbs_obj.decommit = decommit_obj
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                                else:
                                    fbs_obj = FbsOffers.objects.create(
                                        decommit=decommit_obj)
                                    fbs_obj.decommit = decommit_obj
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj
                                    notification_decommit_date = 'raised'
                            else:
                                if fbs_obj != None:
                                    fbs_obj.decommit = None
                                    fbs_obj.save()
                                    player.fbs_offers = fbs_obj

                        if len(school_visits) >= 1:
                            visit_schools_objs = School.objects.filter(
                                name__in=school_visits)
                        if len(school_visits) >= 1:
                            # if fbs_obj == None:
                            visits_obj = SchoolsVisit.objects.create(
                                total=len(school_visits))
                            visit_schools_objs = School.objects.filter(
                                name__in=school_visits)
                            for school_obj in visit_schools_objs:
                                visits_obj.schools.add(school_obj.id)
                            if fbs_obj != None:
                                fbs_obj.visits = visits_obj
                                fbs_obj.save()
                                player.fbs_offers = fbs_obj

                            else:
                                fbs_obj = FbsOffers.objects.create(
                                    visits=visits_obj)
                                player.fbs_offers = fbs_obj
                        else:
                            if fbs_obj != None:
                                fbs_obj.visits = None
                                player.fbs_offers = fbs_obj

                    # player.save()
                    # if commit_date != None and commit_school != None:
                    #     if commit_school != None:
                    #         school_obj = School.objects.get(
                    #             name=commit_school)
                    #         fbs_hardcommit = FbsHardCommit.objects.create(
                    #             commited_on=school_obj,
                    #             school=commit_school
                    #         )
                    #         if fbs_obj != None:
                    #             fbs_obj.hard_commit = fbs_hardcommit
                    # if decommit_date != None and decommit_school != None:
                    #     fbs_decommit = FbsDeCommit.objects.create(
                    #         decommited_on=decommit_date,
                    #         school=decommit_school
                    #     )
                    #     fbs_obj.decommit = fbs_decommit
                    # fbs_obj.save()

                    # if fbs_obj != None:
                    #     fbs_obj.save()
                    #     player.fbs_offers = fbs_obj
                try:
                    if notifications_total_offer_checker == 'raised' or notification_schools_offer_checker == 'raised':
                        myboard_players = MyBoard.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        watchlist_players = WatchList.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        user_ids = []
                        for vals in myboard_players:
                            user_ids.append(vals)
                        for vals in watchlist_players:
                            user_ids.append(vals)

                        unique_user_id = []
                        unique_user_id = list(set(user_ids))

                        for request_user in unique_user_id:
                            try:
                                notification_user = User.objects.get(
                                    id=request_user)
                                notification = Notifications.objects.create(
                                    user=notification_user)
                                notification.notification_type = 'offers'
                                notification.player = player
                                if len(add_count) > 0:
                                    notification.message = "has {} offers added.".format(
                                        len(add_count))
                                else:
                                    notification.message = "has offers updated."
                                notification.save()
                            except Exception as e:
                                print(e)
                except Exception as e:
                    print(e)
                try:
                    if notification_hard_commit_date == 'raised' or notification_hard_commit_school == 'raised':
                        myboard_players = MyBoard.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        watchlist_players = WatchList.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        user_ids = []
                        for vals in myboard_players:
                            user_ids.append(vals)
                        for vals in watchlist_players:
                            user_ids.append(vals)

                        unique_user_id = []
                        unique_user_id = list(set(user_ids))

                        for request_user in unique_user_id:
                            try:
                                notification_user = User.objects.get(
                                    id=request_user)
                                notification = Notifications.objects.create(
                                    user=notification_user)
                                notification.notification_type = 'commit'
                                notification.message = "has a Commitment update"
                                notification.player = player
                                notification.save()
                            except Exception as e:
                                print(e)
                except Exception as e:
                    print(e)
                try:
                    if notification_decommit_school == 'raised' or notification_decommit_date == 'raised':
                        myboard_players = MyBoard.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        watchlist_players = WatchList.objects.filter(
                            player=player).values_list('user__id', flat=True)
                        user_ids = []
                        for vals in myboard_players:
                            user_ids.append(vals)
                        for vals in watchlist_players:
                            user_ids.append(vals)

                        unique_user_id = []
                        unique_user_id = list(set(user_ids))

                        for request_user in unique_user_id:
                            try:
                                notification_user = User.objects.get(
                                    id=request_user)
                                notification = Notifications.objects.create(
                                    user=notification_user)
                                notification.notification_type = 'decommit'
                                notification.message = "has a Decommitment update"
                                notification.player = player
                                notification.save()
                            except Exception as e:
                                print(e)
                except Exception as e:
                    print(e)

                if player.city != None:
                    if player_city != None and player_city != '':
                        p_city = City.objects.filter(
                            name__iexact=player_city
                        )
                        if p_city:
                            player.city = p_city[0]
                    else:
                        player.city = None
                else:
                    if player_city != None and player_city != '':
                        p_city = City.objects.filter(
                            name__iexact=player_city
                        )
                        if p_city:
                            player.city = p_city[0]

                if player.state != None:
                    if player_state != None and player_state != '':
                        p_state = State.objects.get(
                            name__iexact=player_state
                        )
                        player.state = p_state
                    else:
                        player.state = None
                else:
                    if player_state != None and player_state != '':
                        p_state = State.objects.get(
                            name__iexact=player_state
                        )
                        player.state = p_state
                    else:
                        player.state = None

                if player.classification != None:
                    if player_class != None and player_class != '':
                        try:
                            p_class = Classification.objects.get(
                                year__iexact=player_class)
                            player.classification = p_class
                        except Classification.DoesNotExist:
                            p_class = Classification.objects.create(
                                year=player_class)
                            player.classification = p_class
                    else:
                        player.classification = None
                else:
                    if player_class != None and player_class != '':
                        try:
                            p_class = Classification.objects.get(
                                year__iexact=player_class)
                            player.classification = p_class
                        except Classification.DoesNotExist:
                            p_class = Classification.objects.create(
                                year=player_class)
                            player.classification = p_class
                    else:
                        player.classification = None

                    #player.classification = p_class
                # Social Engagement
                p_social_engagement = request.data['social_engagement']
                if p_social_engagement != None and p_social_engagement != '':
                    if p_social_engagement['twitter_handle'] != None and \
                            p_social_engagement['twitter_handle'] != '':
                        plyr_twitter_handle = p_social_engagement['twitter_handle']
                    else:
                        plyr_twitter_handle = None
                    if p_social_engagement['followers'] != None and p_social_engagement['followers'] != '':
                        plyr_twitter_followers = p_social_engagement['followers']
                    else:
                        plyr_twitter_followers = None
                    if p_social_engagement['following'] != None and p_social_engagement['following'] != '':
                        plyr_twitter_following = p_social_engagement['following']
                    else:
                        plyr_twitter_following = None
                    if p_social_engagement['tweets'] != None and p_social_engagement['tweets'] != '':
                        plyr_twitter_tweets = p_social_engagement['tweets']
                    else:
                        plyr_twitter_tweets = None
                    if p_social_engagement['key_people_followers'] != None and \
                            p_social_engagement['key_people_followers'] != '':
                        plyr_twitter_key_ppl_followers = p_social_engagement['key_people_followers']
                    else:
                        plyr_twitter_key_ppl_followers = None
                    if p_social_engagement['key_people_followings'] != None and \
                            p_social_engagement['key_people_followings'] != '':
                        plyr_twitter_key_ppl_following = p_social_engagement['key_people_followings']
                    else:
                        plyr_twitter_key_ppl_following = None
                    if p_social_engagement['retweets'] != None and \
                            p_social_engagement['retweets'] != '':
                        plyr_twitter_retweets = p_social_engagement['retweets']
                    else:
                        plyr_twitter_retweets = None
                    if p_social_engagement['new_followers'] != None and \
                            p_social_engagement['new_followers'] != '':
                        plyr_twitter_new_followers = p_social_engagement['new_followers']
                    else:
                        plyr_twitter_new_followers = None
                    if p_social_engagement['newly_followed'] != None and \
                            p_social_engagement['newly_followed'] != '':
                        plyr_twitter_newly_followed = p_social_engagement['newly_followed']
                    else:
                        plyr_twitter_newly_followed = None
                else:
                    player_social = None

                if player.social_engagement != None:
                    p_twitter = SocialEngagement.objects.get(
                        id=player.social_engagement.id)
                    p_twitter.twitter_handle = plyr_twitter_handle
                    p_twitter.followers = plyr_twitter_followers
                    p_twitter.following = plyr_twitter_following
                    p_twitter.tweets = plyr_twitter_tweets
                    p_twitter.retweets = plyr_twitter_retweets
                    p_twitter.key_people_followers = plyr_twitter_key_ppl_followers
                    p_twitter.key_people_followings = plyr_twitter_key_ppl_following
                    p_twitter.new_followers = plyr_twitter_new_followers
                    p_twitter.newly_followed = plyr_twitter_newly_followed
                    p_twitter.save()
                else:
                    if p_social_engagement != None:
                        p_twitter = SocialEngagement.objects.create(
                            twitter_handle=plyr_twitter_handle,
                            followers=plyr_twitter_followers,
                            following=plyr_twitter_following,
                            tweets=plyr_twitter_tweets,
                            retweets=plyr_twitter_retweets,
                            key_people_followers=plyr_twitter_key_ppl_followers,
                            key_people_followings=plyr_twitter_key_ppl_following,
                            new_followers=plyr_twitter_new_followers,
                            newly_followed=plyr_twitter_newly_followed
                        )
                        player.social_engagement = p_twitter
                    else:
                        player.social_engagement = None
                # Personality Insights
                p_pers_insights = request.data['personality_insight']
                if p_pers_insights != None and p_pers_insights != '':
                    p_pers_insights_personality = p_pers_insights['personality']
                    if p_pers_insights_personality != None:
                        personality_cochability = p_pers_insights_personality['coachability']
                        if personality_cochability:
                            p_personality_cochability = personality_cochability
                        else:
                            p_personality_cochability = None
                        personality_extroverted = p_pers_insights_personality['extroverted']
                        if personality_extroverted:
                            p_personality_extroverted = personality_extroverted
                        else:
                            p_personality_extroverted = None
                        personality_openness = p_pers_insights_personality['openness']
                        if personality_openness:
                            p_personality_openness = personality_openness
                        else:
                            p_personality_openness = None
                        personality_team_player = p_pers_insights_personality['team_player']
                        if personality_team_player:
                            p_personality_team_player = personality_team_player
                        else:
                            p_personality_team_player = None
                        personality_temperament = p_pers_insights_personality['temperament']
                        if personality_temperament:
                            p_personality_temperament = personality_temperament
                        else:
                            p_personality_temperament = None
                    p_pers_insights_values = p_pers_insights['values']
                    if p_pers_insights_values != None:
                        values_achievement = p_pers_insights_values['achievement']
                        if values_achievement:
                            p_values_achievement = values_achievement
                        else:
                            p_values_achievement = None
                        values_helping_others = p_pers_insights_values['helping_others']
                        if values_helping_others:
                            p_values_helping_others = values_helping_others
                        else:
                            p_values_helping_others = None
                        values_stimulation = p_pers_insights_values['stimulation']
                        if values_stimulation:
                            p_values_stimulation = values_stimulation
                        else:
                            p_values_stimulation = None
                        values_takin_pleasure_life = p_pers_insights_values['taking_pleasure_in_life']
                        if values_takin_pleasure_life:
                            p_values_takin_pleasure_life = values_takin_pleasure_life
                        else:
                            p_values_takin_pleasure_life = None
                        values_tradition = p_pers_insights_values['tradition']
                        if values_tradition:
                            p_values_tradition = values_tradition
                        else:
                            p_values_tradition = None
                    p_pers_insights_needs = p_pers_insights['needs']
                    if p_pers_insights_needs != None:
                        needs_challenge = p_pers_insights_needs['challenge']
                        if needs_challenge:
                            p_needs_challenge = needs_challenge
                        else:
                            p_needs_challenge = None
                        needs_excitement = p_pers_insights_needs['excitement']
                        if needs_excitement:
                            p_needs_excitement = needs_excitement
                        else:
                            p_needs_excitement = None
                        needs_ideal = p_pers_insights_needs['ideal']
                        if needs_ideal:
                            p_needs_ideal = needs_ideal
                        else:
                            p_needs_ideal = None
                        needs_stability = p_pers_insights_needs['stability']
                        if needs_stability:
                            p_needs_stability = needs_stability
                        else:
                            p_needs_stability = None
                        needs_structure = p_pers_insights_needs['structure']
                        if needs_structure:
                            p_needs_structure = needs_structure
                        else:
                            p_needs_structure = None

                if player.personality_insight != None:
                    player_pi = PersonalityInsights.objects.get(
                        id=player.personality_insight.id)
                    if player_pi.personality != None:
                        pi_personality = ProspectsPersonality.objects.get(
                            id=player_pi.personality.id)
                        pi_personality.team_player = p_personality_team_player
                        pi_personality.coachability = p_personality_cochability
                        pi_personality.openness = p_personality_openness
                        pi_personality.extroverted = p_personality_extroverted
                        pi_personality.temperament = p_personality_temperament
                        pi_personality.save()
                    if player_pi.values != None:
                        pi_values = ProspectsValues.objects.get(
                            id=player_pi.values.id)
                        pi_values.tradition = p_values_tradition
                        pi_values.stimulation = p_values_stimulation
                        pi_values.helping_others = p_values_helping_others
                        pi_values.achievement = p_values_achievement
                        pi_values.taking_pleasure_in_life = p_values_takin_pleasure_life
                        pi_values.save()
                    if player_pi.needs != None:
                        pi_needs = ProspectsNeeds.objects.get(
                            id=player_pi.needs.id)
                        pi_needs.challenge = p_needs_challenge
                        pi_needs.structure = p_needs_structure
                        pi_needs.stability = p_needs_stability
                        pi_needs.excitement = p_needs_excitement
                        pi_needs.ideal = p_needs_ideal
                        pi_needs.save()

                else:
                    if p_pers_insights != None:
                        if p_pers_insights_needs != None:
                            pi_needs = ProspectsNeeds.objects.create(
                                challenge=p_needs_challenge,
                                structure=p_needs_structure,
                                stability=p_needs_stability,
                                excitement=p_needs_excitement,
                                ideal=p_needs_ideal,
                            )
                        if p_pers_insights_values != None:
                            pi_values = ProspectsValues.objects.create(
                                tradition=p_values_tradition,
                                stimulation=p_values_stimulation,
                                helping_others=p_values_helping_others,
                                achievement=p_values_achievement,
                                taking_pleasure_in_life=p_values_takin_pleasure_life,
                            )
                        if p_pers_insights_personality != None:
                            pi_personality = ProspectsPersonality.objects.create(
                                team_player=p_personality_team_player,
                                coachability=p_personality_cochability,
                                openness=p_personality_openness,
                                extroverted=p_personality_extroverted,
                                temperament=p_personality_temperament,
                            )
                        player_pi = PersonalityInsights.objects.create(
                            personality=pi_personality,
                            values=pi_values,
                            needs=pi_needs,
                        )
                        player.personality_insight = player_pi

                if player.city != None:
                    if player_city != None and player_city != '':
                        city_obj = City.objects.filter(
                            name__iexact=player_city)
                        if city_obj:
                            player.city = city_obj[0]
                    else:
                        player.city = None
                else:
                    if player_city != None and player_city != '':
                        city_obj = City.objects.filter(
                            name__iexact=player_city)
                        if city_obj:
                            player.city = city_obj[0]

                if player.state != None:
                    if player_state != None and player_state != '':
                        state_obj = State.objects.get(
                            name__iexact=player_state)
                        player.state = state_obj
                    else:
                        player.state = None
                else:
                    if player_state != None and player_state != '':
                        state_obj = State.objects.get(
                            name=player_state)
                        player.state = state_obj
                if player.position:
                    player.position.clear()
                    if p_positions:
                        if len(p_positions) >= 1:
                            for pos in p_positions:
                                try:
                                    pos_obj = Positions.objects.get(
                                        name__iexact=pos)
                                    player.position.add(pos_obj)
                                except Exception as e:
                                    print(e)
                if player.school:
                    if player_school != None and player_school != '':
                        school_obj = School.objects.get(
                            name__iexact=player_school)
                        player.school = school_obj
                    else:
                        player.school = None
                else:
                    if player_school != None and player_school != '':
                        school_obj = School.objects.get(
                            name__iexact=player_school)
                        player.school = school_obj
                if player.vertical:
                    if p_vertical:
                        player.vertical = p_vertical
                    else:
                        player.vertical = None
                else:
                    if p_vertical:
                        player.vertical = p_vertical
                if player.short_shuttle:
                    if p_short_shuttle:
                        player.short_shuttle = p_short_shuttle
                    else:
                        player.short_shuttle = None
                else:
                    if p_short_shuttle:
                        player.short_shuttle = p_short_shuttle
                if player.fourty_yard_dash:
                    if p_fourty_yard_dash:
                        player.fourty_yard_dash = p_fourty_yard_dash
                    else:
                        player.fourty_yard_dash = None
                else:
                    if p_fourty_yard_dash:
                        player.fourty_yard_dash = p_fourty_yard_dash
                # if player.profile_photo:
                #     p_avatar = request.data['profile_photo']
                #     player.profile_photo.save(
                #         os.path.basename(img_url),
                #         File(open(p_avatar, 'rb'))
                #     )
                playmaking_analyze = []
                playmaking_analyze.append(p_interception)
                playmaking_analyze.append(p_sack)
                playmaking_analyze.append(p_touchdown)
                playmaking_score = get_playmaking(player, playmaking_analyze)
                athleticism_analyze = {}
                athleticism_analyze['avg_yards_of_seperation'] = p_avg_yards_of_seperation
                athleticism_analyze['avg_closing_speed'] = p_avg_closing_speed
                athleticism_analyze['top_speed'] = p_top_speed
                athleticism_analyze['avg_transition_time'] = p_avg_transition_time
                athleticism_analyze['time_to_top_speed'] = p_time_to_top_speed
                athleticism_sco = get_athleticism(player, athleticism_analyze)
                if player.play_making is None and player.athleticism is None:
                    player.film_grade = None
                    player_role = PlayerType.objects.get(
                        name__iexact='prospect')
                    player.role = player_role
                else:
                    if (player.athleticism is not None) and (player.play_making is not None):
                        film_grade = (player.athleticism +
                                      player.play_making) / 2
                        player.film_grade = film_grade
                    elif (player.athleticism is not None) and (player.play_making is None):
                        film_grade = (player.athleticism + 0) / 2
                        player.film_grade = film_grade
                    elif (player.athleticism is None) and (player.play_making is not None):
                        film_grade = (0 + player.play_making) / 2
                        player.film_grade = film_grade
                    else:
                        player.film_grade = None
                player.save()

            except Player.DoesNotExist:
                return Response({"message": "Player not Found!"})
            except Exception as e:
                print(e)
        # return Response({"message": "Got some data!", "data": request.data})
    return Response({"result": request.data})


# Custom API for Exporting Players from Admin site

def admin_export_view(request):
    result = export_player(request)
    return result


class AdminPlayerExport:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def export_player(request):
    filters = {}
    if 'classification' in request.GET:
        filters['classification__year__iexact'] = request.GET['classification']
    if 'position' in request.GET:
        filters['position__name__iexact'] = request.GET['position']
    if 'player_ids' in request.GET:
        filters['id__in'] = request.GET['player_ids'].split(',')

    admin_section_player = Player.objects.filter(
        **filters,
        role__name__in=['prospect', 'undercruited']
    )

    model = admin_section_player.model

    model_fields = [

        model._meta.get_field('first_name'),
        model._meta.get_field('last_name'),
        model._meta.get_field('classification'),
        model._meta.get_field('position'),
        model._meta.get_field('school'),
        model._meta.get_field('city'),
        model._meta.get_field('state'),
        model._meta.get_field('film_grade'),
        model._meta.get_field('athleticism'),
        model._meta.get_field('play_making'),
        model._meta.get_field('height'),
        model._meta.get_field('weight'),
        model._meta.get_field('fourty_yard_dash'),
        model._meta.get_field('short_shuttle'),
        model._meta.get_field('jersey_number'),
        model._meta.get_field('star_rating'),
        model._meta.get_field('vertical'),

    ]
    model_fields1 = [
        model._meta.get_field('avg_transition_time'),
        model._meta.get_field('avg_yards_of_seperation'),
        model._meta.get_field('top_speed'),
        model._meta.get_field('time_to_top_speed'),
        model._meta.get_field('avg_closing_speed'),
        model._meta.get_field('interception'),
        model._meta.get_field('sack'),
        model._meta.get_field('touchdown'),
    ]

    headers = ['Player Details', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Performance Data', '', '', '', '', '', '', '', 'Social Engagement', '',
               '', '', '', '', '', '', '', 'IntangeAlytics - Personality', '', '', '', '', 'IntangeAlytics - Prospect Needs', '', '', '', '', 'IntangeAlytics - Values', '', '', '', '']

    Display_header = ['First Name', 'Last Name', 'Class', 'Position', 'High School', 'City', 'State',
                      'Film Grade', 'Athleticism', 'Playmaking', 'Height', 'Weight', '40 Yards', 'Short Shuttle', 'Jersey #',
                      'Star Rating', 'Vertical', 'Offers', 'Commit', 'Decommit', 'Visits', 'Avg Tranisition Time', 'Avg Yards of Seperation',
                      'Max Speed', 'Time to Max Speed', 'Avg Closing Speed', 'Interceptions', 'Touchdowns', 'Sacks',
                      'Twitter Handle', 'Followers', 'New Followers', 'Following', 'Number of Retweets',
                      'Key People (Followers)', 'Number of Tweets', 'Newly Followed',
                      'Key People (Following)', 'Team Player', 'Coachability', 'Extroverted', 'Temperment',
                      'Openness', 'Challenge', 'Structure', 'Stability', 'Excitement', 'Ideal', 'Tradition',
                      'Stimulation', 'Achievement', 'Helping Others', 'Taking Pleasure in life']

    headers = ['Player Details', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Performance Data', '', '', '', '', '', '', '', 'Social Engagement', '',
               '', '', '', '', '', '', '', 'IntangeAlytics - Personality', '', '', '', '', 'IntangeAlytics - Prospect Needs', '', '', '', '', 'IntangeAlytics - Values', '', '', '', '']

    Display_header = ['First Name', 'Last Name', 'Class', 'Position', 'High School', 'City', 'State',
                      'Film Grade', 'Athleticism', 'Playmaking', 'Height', 'Weight', '40 Yards', 'Short Shuttle', 'Jersey #',
                      'Star Rating', 'Vertical', 'Offers', 'Commit', 'Decommit', 'Visits', 'Avg Tranisition Time', 'Avg Yards of Seperation',
                      'Max Speed', 'Time to Max Speed', 'Avg Closing Speed', 'Interceptions', 'Sacks', 'Touchdowns',
                      'Twitter Handle', 'Followers', 'New Followers', 'Following', 'Number of Retweets',
                      'Key People (Followers)', 'Number of Tweets', 'Newly Followed',
                      'Key People (Following)', 'Team Player', 'Coachability', 'Extroverted', 'Temperment',
                      'Openness', 'Challenge', 'Structure', 'Stability', 'Excitement', 'Ideal', 'Tradition',
                      'Stimulation', 'Achievement', 'Helping Others', 'Taking Pleasure in life']

    headers1 = [field.name for field in model_fields]
    headers_fbs = [field.name for field in model_fields1]
    fbs_offers = ['offers', 'commit', 'decommit', 'visits']

    headers1 = headers1 + fbs_offers + headers_fbs

    headers1 = headers1 + ['twitter_handle',
                           'followers', 'following', 'new_followers', 'key_people_followers',
                           'key_people_followings',  'tweets', 'retweets', 'newly_followed',
                           'team_player', 'coachability', 'openness', 'extroverted', 'temperament',
                           'challenge', 'structure', 'stability', 'excitement', 'ideal', 'tradition', 'stimulation',
                           'helping_others', 'achievement', 'taking_pleasure_in_life']

    model_fields = model_fields+fbs_offers+model_fields1 + ['twitter_handle',
                                                            'followers', 'following', 'new_followers', 'key_people_followers',
                                                            'key_people_followings',  'tweets', 'retweets', 'newly_followed',
                                                            'team_player', 'coachability', 'openness', 'extroverted', 'temperament',
                                                            'challenge', 'structure', 'stability', 'excitement', 'ideal', 'tradition', 'stimulation',
                                                            'helping_others', 'achievement', 'taking_pleasure_in_life']

    def get_row(obj):
        row = []
        for field in model_fields:
            if type(field) == models.ForeignKey:
                val = getattr(obj, field.name)
                if val:
                    val = str(val)
                else:
                    val = ''
            elif type(field) == models.ManyToManyField:
                val = ', '.join([str(item) for item in getattr(
                    obj, field.name).all()])
            elif type(field) == models.DateTimeField:
                value = getattr(obj, field.name,)
                if value:
                    val = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    val = ''
            else:
                try:
                    if type(field) != str:
                        value = getattr(obj, field.name)
                        if field.name == 'height':
                            if value != None and value >= 0:
                                height_val = value
                                feet_obj = height_val / 12
                                feet = int(math.modf(feet_obj)[1])
                                remainder_value = 12 * feet
                                inches = int(height_val - remainder_value)

                                feet_inches = str(feet) + '\'' + str(inches)
                                val = feet_inches
                            else:
                                val = ''
                    if type(field) != str:
                        if field.name != 'height':
                            if value != '':
                                val = value
                            else:
                                val = ''

                    if type(field) == str:
                        if field == 'offers':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.total != None:
                                    offers_lis = []
                                    f = FbsOffers.objects.filter(id=val.id).values_list(
                                        'schools__name', flat=True)
                                    try:
                                        for entries in f:
                                            if entries != None:
                                                offers_lis.append(entries)
                                        val = offers_lis
                                    except Exception as e:
                                        print(e)
                                        val = ''
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'commit':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.hard_commit != None and val.hard_commit.school != None and val.hard_commit.commited_on != None:
                                    val = str(val.hard_commit.school.name) + ', ' + \
                                        str(val.hard_commit.commited_on)
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'decommit':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                if val.decommit != None:
                                    if val.decommit != None and val.decommit.school != None and val.decommit.decommited_on != None:
                                        val = str(val.decommit.school.name) + ', ' + \
                                            str(val.decommit.decommited_on)
                                    else:
                                        val = ''
                                else:
                                    val = ''
                            else:
                                val = ''
                        elif field == 'visits':
                            val = getattr(obj, 'fbs_offers')
                            if val:
                                visits_lis = []
                                f = SchoolsVisit.objects.filter(
                                    id=val.visits_id).values_list('schools__name', flat=True)
                                try:
                                    for entries in f:
                                        visits_lis.append(entries)
                                    val = visits_lis
                                except Exception as e:
                                    print(e)

                            else:
                                val = ''
                        elif field == 'twitter_handle':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.twitter_handle)
                            else:
                                val = ''
                        elif field == 'followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.followers)
                            else:
                                val = ''
                        elif field == 'following':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.following)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'new_followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.new_followers)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'key_people_followers':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.key_people_followers)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'key_people_followings':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.key_people_followings)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'tweets':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.tweets)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'retweets':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.retweets)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'newly_followed':
                            val = getattr(obj, 'social_engagement')
                            if val:
                                val = str(val.newly_followed)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'team_player':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.team_player)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'coachability':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.coachability)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'openness':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.openness)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'extroverted':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.extroverted)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'temperament':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.personality.temperament)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'challenge':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.challenge)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'structure':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.structure)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'stability':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.stability)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''

                        elif field == 'excitement':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.excitement)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'ideal':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.needs.ideal)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'tradition':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.tradition)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'stimulation':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.stimulation)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'helping_others':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.helping_others)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'achievement':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.achievement)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        elif field == 'taking_pleasure_in_life':
                            val = getattr(obj, 'personality_insight')
                            if val:
                                val = str(val.values.taking_pleasure_in_life)
                                if val == 'None':
                                    val = ''
                            else:
                                val = ''
                        else:
                            val = ''
                except Exception as e:
                    print(e)
            if not val:
                val = ''
            row.append(str(val))
            val = ''
        return row

    def stream(headers, Display_header, players):  # Helper function to inject headers
        if headers:
            yield headers
        if Display_header:
            yield Display_header
        for obj in players:
            yield get_row(obj)
    pseudo_buffer = AdminPlayerExport()
    writer = csv.writer(pseudo_buffer, delimiter='\t')
    response = StreamingHttpResponse(
        (writer.writerow(row)
         for row in stream(headers, Display_header, admin_section_player)),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="players-data.csv"'
    return response


@api_view(['GET'])
def get_position_list(request):
    Results = {}
    db_pos_groups = Positions.objects.filter(
        groups__name__iexact='db'
    ).values_list('name', flat=True)
    rb_pos_groups = Positions.objects.filter(
        groups__name__iexact='rb'
    ).values_list('name', flat=True)
    lb_pos_groups = Positions.objects.filter(
        groups__name__iexact='lb'
    ).values_list('name', flat=True)
    edge_rusher_pos_groups = Positions.objects.filter(
        groups__name__iexact='Edge Rushers'
    ).values_list('name', flat=True)
    r_pos_groups = Positions.objects.filter(
        groups__name__iexact='r'
    ).values_list('name', flat=True)

    Results['results'] = {
        'Defensive Backs': sorted(db_pos_groups),
        'Edge Rushers': sorted(edge_rusher_pos_groups),
        'LineBacker': sorted(lb_pos_groups),
        'Receivers': sorted(r_pos_groups),
        'Running Back': sorted(rb_pos_groups),
    }

    return Response(Results)
