from rest_framework import serializers, status

from .models import (PersonalityInsights, ProspectsNeeds, ProspectsPersonality,
                     ProspectsValues)


class PersonalityInsightSerializer(serializers.ModelSerializer):
    """ Personality Insights model serializer """

    class Meta:
        model = PersonalityInsights
        fields = '__all__'


class GetPersonalityInsightSerializer(serializers.ModelSerializer):
    """ Get Personality Insights model serializer """

    class Meta:
        model = PersonalityInsights
        fields = '__all__'
        depth = 1


class ProspectPersonalitySerializer(serializers.ModelSerializer):
    """ ProspectPersonality model serializer """

    class Meta:
        model = ProspectsPersonality
        fields = '__all__'


class ProspectNeedsSerializer(serializers.ModelSerializer):
    """ ProspectNeeds model serializer """

    class Meta:
        model = ProspectsNeeds
        fields = '__all__'


class ProspectValuesSerializer(serializers.ModelSerializer):
    """ ProspectValues model serializer """

    class Meta:
        model = ProspectsValues
        fields = '__all__'
