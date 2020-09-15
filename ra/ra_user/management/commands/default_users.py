from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from ra.settings.config_ra import main_conf as config
from django.contrib.auth.hashers import make_password
User = get_user_model()


class Command(BaseCommand):

    help = 'Used to add RA users for the app.'

    def handle(self, *args, **options):
        # RA admin users
        users_list = config.get('ADMIN_USERS')

        for users in users_list:
            user, created = User.objects.get_or_create(
                first_name=users['first_name'],
                last_name=users['last_name'],
                is_superuser=True,
                is_staff=True,
                defaults={
                    'username': users['username'],
                    'email': users['email'],
                    'password': users['password'],
                },
            )
            if created:
                user.set_password(user.password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        "{} user added successfully.".format(user.username))
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "{} user already exists.".format(user.username))
                )
