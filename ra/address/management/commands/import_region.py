import io
import re
import xlrd
from django.core.management.base import BaseCommand
from address.models import State, Region, Country


class Command(BaseCommand):
    """
        Use Case: python manage.py import_region
        /home/kapil/Desktop/ra_repo/ra/ra/players/management/commands/region_list.xlsx
    """
    help = 'Used to Importing Regions Data from Excel File.'

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
                - FURTHER IF MORE UNIVERSITY AND Rigion DATA NEED TO BE ADDED COMMENT
                  DELETE SCRIPT
        """
        country_obj = Country.objects.get(name='USA')
        try:
            for regions in data:
                region = regions[0]
                region_obj, created = Region.objects.get_or_create(
                    name=region.strip().title()
                )
                region_obj.save()
                if region_obj:
                    for state in regions[1:]:
                        if state is not '':
                            try:
                                state_obj = State.objects.get(
                                    name__iexact=state.strip().title(),
                                    # country=country_obj
                                )
                                if state_obj:
                                    state_obj.region = region_obj
                                    state_obj.save()

                            except State.DoesNotExist:
                                state_obj = State.objects.create(
                                    name=state.strip().title(),
                                    region=region_obj)
                                state_obj.save()

        except Exception as e:
            print(e)
