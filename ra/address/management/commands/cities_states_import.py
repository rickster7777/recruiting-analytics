import io
import re
import xlrd
from django.core.management.base import BaseCommand
from address.models import City, State, Country


class Command(BaseCommand):
    """
        Use Case: python manage.py cities_states_import
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/statelist.xlsx
    """
    help = 'Used to Importing City and States Data from Excel File.'

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
        City.objects.all().delete()
        State.objects.all().delete()
        print('Deleting Cities and States data.......')
        print('Adding Cities and States data.......')
        country_obj = Country.objects.get(name='USA')
        try:
            for states_cities in data:
                state_name = states_cities[0]
                state_abbrv = states_cities[1]

                state_obj, created = State.objects.get_or_create(
                    name=state_name.strip().title(),
                    abbreviation=state_abbrv.upper().strip(),
                    country=country_obj
                )

                for city in states_cities[2:]:
                    if city is not '':
                        try:
                            city_obj = City.objects.get(
                                name__iexact=city.strip().title(),
                                state=state_obj,
                            )
                        except City.DoesNotExist:
                            city_obj = City.objects.create(
                                name=city.strip().title(),
                                state=state_obj,
                            )

        except Exception as e:
            print(e)
