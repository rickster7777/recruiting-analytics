# Generated by Django 2.2.5 on 2019-11-01 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0009_player_film_grade'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classification',
            old_name='name',
            new_name='year',
        ),
    ]
