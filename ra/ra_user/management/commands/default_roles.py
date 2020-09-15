"""
Management utility to create user roles for uc-admin and university-admin.

Example usage:
  manage.py create_user_roles
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Used to create a User Roles for Admin and Coach.'

    def handle(self, *args, **options):
        roles = ['coach', 'admin']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Role {} created successfully.".format(role)
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR("Role {} already added.".format(role)))
