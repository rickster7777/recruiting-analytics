# Generated by Django 2.2.5 on 2019-11-20 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0027_auto_20191119_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fbshardcommit',
            name='commited_on',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]