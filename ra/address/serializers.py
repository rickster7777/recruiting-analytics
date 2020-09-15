from rest_framework import serializers

from .models import Address, City, State, School, Region, College, Country


class AddressSerializer(serializers.ModelSerializer):
    """ Address model serializer """

    class Meta:
        model = Address
        fields = '__all__'


class GetAddressSerializer(serializers.ModelSerializer):
    """ Address model serializer """

    class Meta:
        model = Address
        fields = '__all__'
        depth = 3


class CitySerializer(serializers.ModelSerializer):
    """ City model serializer """

    class Meta:
        model = City
        fields = '__all__'


class GetCitySerializer(serializers.ModelSerializer):
    """ City model serializer """

    class Meta:
        model = City
        fields = '__all__'
        depth = 2


class StateSerializer(serializers.ModelSerializer):
    """ State model serializer """

    class Meta:
        model = State
        fields = '__all__'


class GetStateSerializer(serializers.ModelSerializer):
    """ State model serializer """

    class Meta:
        model = State
        fields = '__all__'
        depth = 2


class RegionSerializer(serializers.ModelSerializer):
    """ Region model serializer """

    class Meta:
        model = Region
        fields = '__all__'


class SchoolSerializer(serializers.ModelSerializer):
    """ School model serializer """

    class Meta:
        model = School
        fields = '__all__'


class GetSchoolSerializer(serializers.ModelSerializer):
    """ School model serializer """

    class Meta:
        model = School
        fields = '__all__'
        depth = 2


class CollegeSerializer(serializers.ModelSerializer):
    """ College model serializer """

    class Meta:
        model = College
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `College` instance in already exist or not,
        given the validated data.
        """
        college_name = validated_data['name'].strip()
        city_obj = validated_data['city']
        state_obj = validated_data['state']
        # city_obj = City.objects.get(id=city_id)
        # state_obj = State.objects.get(id=state_id)
        try:
            college_obj = College.objects.get(
                name__iexact=college_name,
                city__name__iexact=city_obj.name,
                state__name__iexact=state_obj.name
            )
            if college_obj:
                raise serializers.ValidationError({
                    'error': college_name + ' already exist with id of ' + str(college_obj.id)
            })
        except College.DoesNotExist:
            validated_data['name'] = college_name.title().strip()
            return College.objects.create(**validated_data)


class GetCollegeSerializer(serializers.ModelSerializer):
    """ College model serializer """

    class Meta:
        model = College
        fields = '__all__'
        depth = 3


class CountrySerializer(serializers.ModelSerializer):
    """ Country model serializer """

    class Meta:
        model = Country
        fields = '__all__'
