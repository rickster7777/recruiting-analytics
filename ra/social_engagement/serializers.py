from .models import SocialEngagement
from rest_framework import serializers


class SocialEngagementSerializer(serializers.ModelSerializer):
    """ SocialEngagement Serializer """

    class Meta:
        model = SocialEngagement
        fields = '__all__'
