import io
import re
import xlrd
from django.core.management.base import BaseCommand
from address.models import City, State, Country, College


class Command(BaseCommand):
    """
        Use Case: python manage.py add_colleges
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/statelist.xlsx
    """
    help = 'Used to Importing Colleges Data from Excel File.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        data = []
        xlsx_file = xlrd.open_workbook(options['file'])
        worksheet = xlsx_file.sheet_by_index(0)
        offset = 0
        for i, row in enumerate(range(worksheet.nrows)):
            if i <= offset:
                continue
            row_data = []
            for j, col in enumerate(range(1, worksheet.ncols+1)):
                row_data.append(worksheet.cell_value(i, j))
            data.append(row_data)

        """
            Developer Comment:-
                - BELOW DELETE SCRIPT RUN ONLY FIRST TIME.
                - FURTHER IF MORE UNIVERSITY AND IPEDS DATA NEED TO BE ADDED COMMENT
                  DELETE SCRIPT
        """
        # City.objects.all().delete()
        # State.objects.all().delete()
        # print('Deleting Cities and States data.......')
        # print('Adding Cities and States data.......')
        College.objects.all().delete()
        try:
            country_obj = Country.objects.get(name='USA')
            for college_data in data:
                college_raw_name = college_data[0].title().strip()
                college_name = college_raw_name
                city_raw_name = college_data[1].title().strip()
                city_name = city_raw_name
                state_raw_name = college_data[2].title().strip()
                state_name = state_raw_name
                try:
                    state_obj = State.objects.get(
                        name__iexact=state_name.strip(),
                        country=country_obj
                    )
                    state_obj.country = country_obj
                    state_obj.save()
                except State.DoesNotExist:
                    try:
                        state_obj = State.objects.get(
                            name=state_name.strip()
                        )
                    except State.DoesNotExist:
                        state_obj = State.objects.create(
                            name=state_name.strip()
                        )
                try:
                    city_obj = City.objects.get(
                        name__iexact=city_name,
                        state=state_obj,
                    )
                except City.DoesNotExist:
                    try:
                        city_obj = City.objects.get(
                            name=city_name.strip()
                        )
                    except City.DoesNotExist:
                        city_obj = City.objects.create(
                            name=city_name.strip()
                        )
                college_obj, created = College.objects.get_or_create(
                    name=college_name,
                    city=city_obj,
                    state=state_obj
                )
                if created:
                    print("college added successful", college_name)
                else:
                    print("already exists in db", college_name)

        except Exception as e:
            print(e)
