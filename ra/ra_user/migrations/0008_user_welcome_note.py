# Generated by Django 2.2.5 on 2019-11-04 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ra_user', '0007_userotp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='welcome_note',
            field=models.BooleanField(default=False),
        ),
    ]
