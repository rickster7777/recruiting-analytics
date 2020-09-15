"""
Management utility to add sites.
"""
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Used to add Site.'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('domain', type=str)

    def handle(self, *args, **options):

        site = Site.objects.filter(domain='example.com')
        if site:
            site[0].delete()

        Site.objects.get_or_create(
            name=options['name'],
            domain=options['domain']
        )
        self.stdout.write(
            self.style.SUCCESS(
                "{} site added successfully.".format(options['name'])
            )
        )
