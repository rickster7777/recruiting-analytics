from django.shortcuts import render
from rest_framework import filters, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (PersonalityInsights, ProspectsNeeds, ProspectsPersonality,
                     ProspectsValues)
from .serializers import (GetPersonalityInsightSerializer,
                          PersonalityInsightSerializer,
                          ProspectNeedsSerializer,
                          ProspectPersonalitySerializer,
                          ProspectValuesSerializer)


class PIPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class PersonalityInsightViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing PersonalityInsight of Player.
    create:
        Create a new PersonalityInsight instance.
    retrieve:
        Return the given PersonalityInsight.
    update:
        Update the given PersonalityInsight.
    partial_update:
        Update the given PersonalityInsight given field only.
    destroy:
        Delete the given PersonalityInsight.
   """
    pagination_class = PIPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalityInsightSerializer
    queryset = PersonalityInsights.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetPersonalityInsightSerializer
        else:
            return PersonalityInsightSerializer


class ProspectPersonalityViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing ProspectPersonality of Player.
    create:
        Create a new ProspectPersonality instance.
    retrieve:
        Return the given ProspectPersonality.
    update:
        Update the given ProspectPersonality.
    partial_update:
        Update the given ProspectPersonality given field only.
    destroy:
        Delete the given ProspectPersonality.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProspectPersonalitySerializer
    queryset = ProspectsPersonality.objects.all()


class ProspectNeedsViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing ProspectNeeds of Player.
    create:
        Create a new ProspectNeeds instance.
    retrieve:
        Return the given ProspectNeeds.
    update:
        Update the given ProspectNeeds.
    partial_update:
        Update the given ProspectNeeds given field only.
    destroy:
        Delete the given ProspectNeeds.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProspectNeedsSerializer
    queryset = ProspectsNeeds.objects.all()


class ProspectValuesViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing ProspectValues of Player.
    create:
        Create a new ProspectValues instance.
    retrieve:
        Return the given ProspectValues.
    update:
        Update the given ProspectValues.
    partial_update:
        Update the given ProspectValues given field only.
    destroy:
        Delete the given ProspectValues.
   """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProspectValuesSerializer
    queryset = ProspectsValues.objects.all()
