import os
import urllib.request as urllib2
from os import environ
from rest_framework import serializers
from rest_framework.response import Response
from django.core.files import File
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from .models import Address, City, College, Country, Region, School, State
from .serializers import (AddressSerializer, CitySerializer, CollegeSerializer,
                          CountrySerializer, GetAddressSerializer,
                          GetCitySerializer, GetCollegeSerializer,
                          GetSchoolSerializer, GetStateSerializer,
                          RegionSerializer, SchoolSerializer, StateSerializer)
from django.http import HttpResponse
import csv

class AddressViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing addresses.
    create:
        Create a new address instance.
    retrieve:
        Return the given address.
    update:
        Update the given address.
    partial_update:
        Update the given address given field only.
    destroy:
        Delete the given address.
   """

    # permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetAddressSerializer
        else:
            return AddressSerializer


class CityViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing cities.
    create:
        Create a new city instance.
    retrieve:
        Return the given city.
    update:
        Update the given city.
    partial_update:
        Update the given city given field only.
    destroy:
        Delete the given city.
   """

    # permission_classes = (IsAuthenticated,)
    pagination_class = None
    serializer_class = CitySerializer
    queryset = City.objects.all().order_by('name').distinct()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name',
                       )
    search_fields = (
        'name',
        'state__name',
    )

    # filters fields not accessible when FilterSet Used
    filter_fields = {
        'id': ['exact'],
        'name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__abbreviation': ['iexact', 'icontains', 'istartswith', 'in', 'isnull']
    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetCitySerializer
        else:
            return CitySerializer


class StateViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing states.
    create:
        Create a new state instance.
    retrieve:
        Return the given state.
    update:
        Update the given state.
    partial_update:
        Update the given state given field only.
    destroy:
        Delete the given state.
   """

    # permission_classes = (IsAuthenticated,)
    pagination_class = None
    serializer_class = StateSerializer
    queryset = State.objects.all().order_by('name').distinct()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name'
                       )
    search_fields = (
        'name',
        'region__name',
    )

    # filters fields not accessible when FilterSet Used
    filter_fields = {
        'id': ['exact'],
        'name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'region__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
    }

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetStateSerializer
        else:
            return StateSerializer


class SchoolsPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class SchoolViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing schools.
    create:
        Create a new school instance.
    retrieve:
        Return the given school.
    update:
        Update the given school.
    partial_update:
        Update the given school given field only.
    destroy:
        Delete the given school.
   """
    pagination_class = SchoolsPagination
    # permission_classes = (IsAuthenticated,)
    serializer_class = SchoolSerializer
    queryset = School.objects.all().order_by('name').distinct()

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name'
                       )

    filter_fields = {
        'id': ['exact', 'in'],
        'name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],

    }

    def get_queryset(self):
        if self.request.query_params.get('delete_schools'):
            school_ids = self.request.query_params.get('delete_schools')
            ids = school_ids.split(',')
            schools = School.objects.filter(id__in=ids).delete()
            queryset = School.objects.none()
        else:
            queryset = School.objects.all().order_by('name')
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetSchoolSerializer
        else:
            return SchoolSerializer


class RegionViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing region.
    create:
        Create a new region instance.
    retrieve:
        Return the given region.
    update:
        Update the given region.
    partial_update:
        Update the given region given field only.
    destroy:
        Delete the given region.
   """

    # permission_classes = (IsAuthenticated,)
    serializer_class = RegionSerializer
    queryset = Region.objects.all().order_by('name').distinct()


class CollegeViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing College.
    create:
        Create a new College instance.
    retrieve:
        Return the given College.
    update:
        Update the given College.
    partial_update:
        Update the given College given field only.
    destroy:
        Delete the given College.
    """

    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    )

    ordering_fields = ('id',
                       'name',
                       'state__name',
                       'city__name',
                       )

    filter_fields = {
        'id': ['exact', 'in'],
        'name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__country__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'state__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],
        'city__name': ['iexact', 'icontains', 'istartswith', 'in', 'isnull'],

    }

    pagination_class = SchoolsPagination
    # permission_classes = (IsAuthenticated,)
    serializer_class = CollegeSerializer
    queryset = College.objects.all().order_by('name').distinct()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return GetCollegeSerializer
        else:
            return CollegeSerializer

    def get_queryset(self):
        if self.request.query_params.get('delete_colleges'):
            college_ids = self.request.query_params.get(
                'delete_colleges').split(',')
            college = College.objects.filter(id__in=college_ids).delete()
            queryset = College.objects.none()
        else:
            queryset = College.objects.all()
        return queryset

    # def create(self, serializer):

    #     college_id = self.request.data['id']
    #     college_name = self.request.data['name']
    #     city_id = self.request.data['city']
    #     state_id = self.request.data['state']
    #     address_id = self.request.data['address']


    def partial_update(self, request, pk=None):
        college_obj = College.objects.get(id=pk)
        college_name = self.request.data['name']
        city_id = self.request.data['city']
        state_id = self.request.data['state']
        address_id = self.request.data['address']
        city_obj = City.objects.get(id=city_id)
        state_obj = State.objects.get(id=state_id)
        try:
            check_exist_clg = College.objects.get(
                name__iexact=college_name,
                city__name__iexact=city_obj.name,
                state__name__iexact=state_obj.name
            )
            if check_exist_clg:
                if check_exist_clg.id == college_obj.id:
                    college_obj.name = college_name.strip().title()
                    if address_id != None:
                        addr_obj = Address.objects.get(id=address_id)
                        college_obj.address = addr_obj
                    college_obj.city = city_obj
                    college_obj.state = state_obj
                    college_obj.save()
                    college_data = GetCollegeSerializer(college_obj).data
                    return Response(college_data)
                else:
                    raise serializers.ValidationError({
                            'error': college_name + ' already exist with id of ' + str(check_exist_clg.id)
                    })
        except College.DoesNotExist:
            college_obj.name = college_name.strip().title()
            if address_id != None:
                addr_obj = Address.objects.get(id=address_id)
                college_obj.address = addr_obj
            college_obj.city = city_obj
            college_obj.state = state_obj
            college_obj.save()
            college_data = GetCollegeSerializer(college_obj).data
            return Response(college_data)


class CountryViewSet(viewsets.ModelViewSet):
    """
    list:
        Return a list of all the existing Country.
    create:
        Create a new Country instance.
    retrieve:
        Return the given Country.
    update:
        Update the given Country.
    partial_update:
        Update the given Country given field only.
    destroy:
        Delete the given Country.
   """

    # permission_classes = (IsAuthenticated,)
    serializer_class = CountrySerializer
    queryset = Country.objects.all().order_by('name').distinct()


def export_college_csv(request):
    filters = {}
    if 'college_ids' in request.GET:
        filters['id__in'] = request.GET['college_ids'].split(',')
        college_list = College.objects.filter(
            **filters
            )
    else:
        college_list = College.objects.all()

    outer_lis = []
    for college in college_list:
        try:
            college_lis = []
            if college.name:
                name = college.name
            if college.city:
                city = college.city.name
            else:
                city = None
            if college.state:
                state = college.state.name
            else:
                state = None
            college_lis.append(name)
            college_lis.append(state)
            college_lis.append(city)
            if college.address:
                if college.address.street_line_1:
                    street_1 = college.address.street_line_1
                else:
                    street_1 = None
                if college.address.street_line_2:
                    street_2 = college.address.street_line_2
                else:
                    street_2 = None

                if college.address.zip_code:
                    zip_code = college.address.zip_code
                else:
                    zip_code = None
                if college.address.phone:
                    phone = college.address.phone
                else:
                    phone = None
                college_lis.append(zip_code)
                college_lis.append(phone)
                college_lis.append(street_1)
                college_lis.append(street_2)
                #outer_lis.append(college_lis)
            else:
                zip_code = None
                phone = None
                street_1 = None
                street_2 =None

                college_lis.append(zip_code)
                college_lis.append(phone)
                college_lis.append(street_1)
                college_lis.append(street_2)
            outer_lis.append(college_lis)

        except Exception as e:
            print(e)
    headers = ['School Name','state','city','Zip','Phone','Street 1','Street 2']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_user_export.csv"'
    writer = csv.writer(response,delimiter='\t')
    writer.writerow(headers)
    writer.writerows(outer_lis)
    return response


def export_school_csv(request):
    filters = {}
    if 'school_ids' in request.GET:
        filters['id__in'] = request.GET['school_ids'].split(',')
        school_list = School.objects.filter(
            **filters
            )
    else:
        school_list = School.objects.all()
    outer_lis = []
    for school in school_list:
        try:
            school_lis = []
            if school.name:
                name = school.name
            else:
                name = None
            if school.logo:
                logo = school.logo
            else:
                logo = None
            school_lis.append(name)
            school_lis.append(logo)
            outer_lis.append(school_lis)
        except Exception as e:
            print(e)
    headers = ['School Name','Logo']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_user_export.csv"'
    writer = csv.writer(response,delimiter='\t')
    writer.writerow(headers)
    try:
        writer.writerows(outer_lis)
    except Exception as e:
        print(e)
    return response



    #pass
@api_view(['GET', 'POST', 'PUT'])
def school_add_update_view(request):
    if request.method == 'GET':
        print('GET Method')
    if request.method == 'POST':
        sch_name = request.data['name']
        if sch_name != (None or ''):
            sch_nm = sch_name.title()
        else:
            sch_nm = None
        raw_logo = request.data['logo']
        if raw_logo != (None or ''):
            sch_logo = raw_logo
        else:
            sch_logo = None
        if sch_nm != None:
            try:
                sch_obj = School.objects.get(name__iexact=sch_name)
                if sch_logo != None:
                    result = urllib2.urlretrieve(sch_logo)
                    sch_obj.logo.save(
                        os.path.basename(sch_logo),
                        File(open(result[0], 'rb'))
                    )
                    sch_obj.save()
                else:
                    sch_obj.logo = None
                    sch_obj.save()
            except School.DoesNotExist:
                sch_obj = School.objects.create(name=sch_name)
                if sch_logo != None:
                    if sch_logo != None:
                        result = urllib2.urlretrieve(sch_logo)
                        sch_obj.logo.save(
                            os.path.basename(sch_logo),
                            File(open(result[0], 'rb'))
                        )
                        sch_obj.save()
                else:
                    sch_obj.logo = None
                    sch_obj.save()
    if request.method == 'PUT':
        sch_name = request.data['name']
        if sch_name != (None or ''):
            sch_nm = sch_name.title()
        else:
            sch_nm = None
        raw_logo = request.data['logo']
        sch_id = request.data['id']
        if raw_logo != (None or ''):
            sch_logo = raw_logo
        else:
            sch_logo = None
        if sch_nm != None:
            sch_obj = School.objects.get(id=sch_id)
            sch_obj.name = sch_nm
            if sch_logo != None:
                try:
                    result = urllib2.urlretrieve(sch_logo)
                    sch_obj.logo.save(
                        os.path.basename(sch_logo),
                        File(open(result[0], 'rb'))
                    )
                    sch_obj.save()
                except Exception as e:
                    print(e)
            else:
                sch_obj.logo = None
        sch_obj.save()

    return Response({"result": request.data})
