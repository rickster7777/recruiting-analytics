# Generated by Django 2.2.5 on 2019-11-26 06:35

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ra_user', '0009_auto_20191108_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='save_search_names',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
    ]
