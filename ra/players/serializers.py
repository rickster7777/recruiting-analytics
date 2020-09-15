import json
import math

from django.db.models import F, Q
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response

# from ra_user.models import MyBoard, Watchlist
from ra_user.models import MyBoard, WatchList, User
from personality_insights.models import (PersonalityInsights, ProspectsNeeds, ProspectsPersonality,
                     ProspectsValues)
from ra_user.serializers import GetUserSerializer

from .models import (Classification, FbsHardCommit, FbsOffers, Notes, Player,
                     PlayerType, PositionGroup, Positions, SavedSearch,
                     SchoolsVisit, FbsDeCommit, Comments, FbsSchools)
from address.serializers import GetSchoolSerializer
from address.models import School


class PlayerPersonalityInsightSerializer(serializers.ModelSerializer):
    """ Player Personality Insights model serializer """

    class Meta:
        model = PersonalityInsights
        fields = '__all__'
        depth = 1
        read_only_fields = ('personality', 'needs', 'values', )

class FbsDeCommitSerializer(serializers.ModelSerializer):
    """ FbsDeCommit model serializer """

    class Meta:
        model = FbsDeCommit
        fields = '__all__'


class GetPersonalityInsightSerializer(serializers.ModelSerializer):
    """ Get Personality Insights model serializer """

    class Meta:
        model = PersonalityInsights
        fields = '__all__'
        depth = 1

class PlayerTypeSerializer(serializers.ModelSerializer):
    """ Player Type model serializer """

    class Meta:
        model = PlayerType
        fields = '__all__'


class ClassificationSerializer(serializers.ModelSerializer):
    """ Classification model serializer """

    class Meta:
        model = Classification
        fields = '__all__'


class PositionsSerializer(serializers.ModelSerializer):
    """ Position model serializer """

    class Meta:
        model = Positions
        fields = '__all__'


class GetPositionSerializer(serializers.ModelSerializer):
    """ Get Player model serializer """

    class Meta:
        model = Positions
        fields = '__all__'
        depth = 1
        read_only_fields  =(fields, )


class PositionGroupSerializer(serializers.ModelSerializer):
    """ Position Group model serializer """

    class Meta:
        model = PositionGroup
        fields = '__all__'


class NotesSerializer(serializers.ModelSerializer):
    """ Notes model serializer """
    # player_id = serializers.CharField(max_length=200)

    # def create(self, validated_data):
    #     player = Player.objects.get(id=validated_data['player_id'])
    #     remove_player_id = validated_data.pop('player_id')
    #     return Notes.objects.create(**validated_data)

    class Meta:
        model = Notes
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    """ CustomUserSerializer model serializer  """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email',
                  'groups', 'is_active', 'title', 'cell_phone', )
        read_only_fields = (fields, )
        depth = 1


class CommentSerializer(serializers.ModelSerializer):
    """ Comment model serializer """
    class Meta:
        model = Comments
        fields = '__all__'


class GetCommentSerializer(serializers.ModelSerializer):
    """ Get Comment model serializer """
    commented_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = '__all__'
        depth = 1
        read_only_fields = (fields, )


class GetNotesSerializer(serializers.ModelSerializer):
    """ Get NotesSerializer model serializer """
    created_by = CustomUserSerializer(read_only=True)
    comments = GetCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Notes
        fields = '__all__'
        dept = 1
        read_only_fields = (fields, )


class PostNotesSerializer(serializers.ModelSerializer):
    """ Post NotesSerializer model serializer """
    player_id = serializers.UUIDField()

    class Meta:
        model = Notes
        fields = '__all__'


class VisitsSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        exclude = ('address', )
        read_only_fields = ('name', 'logo', )


class SchoolsVisitSerializer(serializers.ModelSerializer):
    """ SchoolsVisit model serializer """

    class Meta:
        model = SchoolsVisit
        fields = '__all__'


class GetSchoolsVisitSerializer(serializers.ModelSerializer):
    """ Get SchoolsVisit model serializer """
    schools = VisitsSchoolSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolsVisit
        fields = '__all__'
        read_only_fields = (fields, )


class FbsHardCommitSerializer(serializers.ModelSerializer):
    """ FbsHardCommit model serializer """

    class Meta:
        model = FbsHardCommit
        fields = '__all__'


class GetFbsHardCommitSerializer(serializers.ModelSerializer):
    """ Get FbsHardCommit model serializer """
    school = VisitsSchoolSerializer(read_only=True)
    class Meta:
        model = FbsHardCommit
        fields = '__all__'
        depth = 1


class FbsOffersSerializer(serializers.ModelSerializer):
    """ FbsOffers model serializer """

    class Meta:
        model = FbsOffers
        fields = '__all__'


class FbsSchoolsSerializer(serializers.ModelSerializer):
    """ FbsSchools model serializer """

    class Meta:
        model = FbsSchools
        fields = '__all__'
        # exclude= ('id', 'fbs_offer',)


class GETFbsSchoolsSerializer(serializers.ModelSerializer):
    """ FbsSchools model serializer """
    school = VisitsSchoolSerializer(read_only=True)
    class Meta:
        model = FbsSchools
        # fields = '__all__'
        exclude = ('fbs_offer',)
        depth = 1


class GetFbsOffersSerializer(serializers.ModelSerializer):
    """ Get FbsOffers model serializer """
    visits = GetSchoolsVisitSerializer(read_only=True)
    schools = GETFbsSchoolsSerializer(
        source="fbsschools_set", many=True, read_only=True)
    # schools = serializers.SerializerMethodField()

    # def get_schools(self, obj):
    #     fbs_school_objs = FbsSchools.objects\
    #         .filter(fbs_offer=obj)\
    #         .order_by('added_on').values_list('school__id')
    #     schools_data = []

    #     for id in fbs_school_objs:
    #         schools_data.append(GetSchoolSerializer(
    #             School.objects.get(id=id[0])).data)
    #     return schools_data
    class Meta:
        model = FbsOffers
        fields = '__all__'
        depth = 2
        read_only_fields = (fields, )


class SavedSearchSerializer(serializers.ModelSerializer):
    """ SavedSearch model serializer """
    # search_by = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )

    class Meta:
        model = SavedSearch
        fields = '__all__'

    # def create(self, validated_data):
    #     """
    #     Create and return a new `SavedSearch` instance if count is less than 5 per User.
    #     """
    #     search_result = SavedSearch.objects.filter(
    #         search_by=validated_data['search_by']
    #     )
    #     if len(search_result) < 5:
    #         return SavedSearch.objects.create(**validated_data)
    #     else:
    #         raise serializers.ValidationError(
    #             {
    #                 "error": "Rate Limit Exceeded",
    #                 "status": 403,
    #                 "message": "You have only save upto 5 searches."
    #             }
    #         )

    def create(self, validated_data):

        search_name = validated_data['name']
        if not SavedSearch.objects.filter(
                search_by__username=validated_data['search_by'].username,
                name__iexact=validated_data['name']).exists():

            return SavedSearch.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(
                {
                    'error': "Duplicate Name found in existing Save Search for requested user",
                    'status': 500
                }
            )

    def update(self, instance, validated_data):
        search_name = validated_data['name']
        if search_name.lower() == instance.name.lower():
            instance.name = search_name.title()
            instance.fitfinder_search = validated_data.get('fitfinder_search')
            instance.save()
            return instance
        elif not SavedSearch.objects.filter(
                search_by__username=validated_data['search_by'].username,
                name__iexact=validated_data['name']).exists():
            instance.name = validated_data.get('name', instance.name)
            instance.fitfinder_search = validated_data.get('fitfinder_search')
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                {
                    'error': "Duplicate Name found in existing Save Search for requested user",
                    'status': 500
                }
            )


class GetSavedSearchSerializer(serializers.ModelSerializer):
    """ Get SavedSearch model serializer """
    search_by = GetUserSerializer()

    class Meta:
        model = SavedSearch
        fields = '__all__'
        depth = 2


class PlayerSerializer(serializers.ModelSerializer):
    """ Player model serializer """
    profile_photo = serializers.FileField(max_length=None, use_url=True,
                                          required=False, allow_null=True)

    class Meta:
        model = Player
        fields = '__all__'

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related('position',
                                             'notes',
                                             )
        queryset = queryset.select_related('role', 'school', 'classification',
                                           'city', 'state', 'fbs_offers',
                                           'personality_insight', 'team',
                                           'social_engagement', )
        return queryset


class GetPlayerSerializer(serializers.ModelSerializer):
    """ Get Player model serializer """
    personality_insight = PlayerPersonalityInsightSerializer(read_only=True)
    fbs_offers = GetFbsOffersSerializer(read_only=True)
    notes = GetNotesSerializer(many=True, read_only=True)
    position = GetPositionSerializer(many=True, read_only=True)
    school = VisitsSchoolSerializer(read_only=True)
    profile_photo = serializers.FileField()
    pin_user_watchlist = serializers.SerializerMethodField()
    pin_user_board = serializers.SerializerMethodField()
    matching_undercruited_count = serializers.SerializerMethodField(
        'get_matching_undercruited_count'
    )
    user_note = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related('position',
                                             'notes',
                                             )
        queryset = queryset.select_related('role', 'school', 'classification',
                                           'city', 'state', 'fbs_offers',
                                           'personality_insight', 'team',
                                           'social_engagement', )
        return queryset

    def get_height(self, player):
        # if player.role.name == 'nfl':
        if player.height != None and player.height >= 0:
            height_val = player.height
            feet_obj = height_val / 12
            feet = int(math.modf(feet_obj)[1])
            remainder_value = 12 * feet
            inches = int(height_val - remainder_value)

            feet_inches = str(feet) + '.' + str(inches)
            return feet_inches
        else:
            return None

    def get_user_note(self, player):
        request_user = self._context['request'].user
        user_group = User.objects.filter(
            username=request_user.username
        ).values_list('groups__name', flat=True)
        if 'coach' in user_group and request_user.college_address is not None \
                and request_user.college_address.name is not None:
            user_notes = Notes.objects.select_related('created_by').prefetch_related('comments').filter(
                created_by__college_address__name=request_user.college_address.name,
                id__in=player.notes.all())
        else:
            user_notes = None
        if user_notes:
            return getattr(player, 'user_note', True)
        else:
            return getattr(player, 'user_note', False)

    def get_pin_user_watchlist(self, player):
        request_user = self._context['request'].user
        user_watchlist = WatchList.objects.select_related('user', 'player').filter(
            user=request_user,
            player__id=player.id)
        if user_watchlist:
            return getattr(player, 'pin_user_watchlist', True)
        else:
            return getattr(player, 'pin_user_watchlist', False)

    def get_pin_user_board(self, player):
        request_user = self._context['request'].user
        user_board = MyBoard.objects.select_related('user', 'player').filter(
            user=request_user,
            player__id=player.id)
        if user_board:
            return getattr(player, 'pin_user_board', True)
        else:
            return getattr(player, 'pin_user_board', False)

    def get_matching_undercruited_count(self, player):
        nfl_filmgrade = player.film_grade
        nfl_height = player.height
        nfl_weight = player.weight
        if player.role != None and player.role.name == 'nfl' and\
                nfl_filmgrade != None and\
                nfl_height != None and\
                nfl_weight != None:

            q_params = self._context['view'].request.query_params
            filters = {}
            for filter in q_params:
                if filter == 'classification':
                    filters['classification__year__iexact'] = q_params[filter]
                if filter == 'position__groups__name__iexact':
                    filters['position__groups__name__iexact'] = q_params[filter]

            filters['film_grade__isnull'] = False
            filters['height__isnull'] = False
            filters['weight__isnull'] = False
            matching_prospects_count = Player.objects.only(
                'role', 'film_grade', 'height', 'weight', 'classification',
                'position').filter(
                Q(
                    Q(**filters) &
                    Q(role__name__iexact='undercruited') &
                    Q(film_grade__lte=nfl_filmgrade + 3.0) &
                    Q(film_grade__gte=nfl_filmgrade - 3.0)
                ) &
                Q(
                    (
                        Q(height__lte=nfl_height + 1) &
                        Q(height__gte=nfl_height - 1)
                    ) &
                    (
                        Q(weight__lte=nfl_weight + 15) &
                        Q(weight__gte=nfl_weight - 15)
                    )
                )
            ).distinct().count()
            return matching_prospects_count
        return 0

    class Meta:
        model = Player
        fields = '__all__'
        depth = 2
        read_only_fields = (fields, )
