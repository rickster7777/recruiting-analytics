# Generated by Django 2.2.5 on 2019-11-27 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0030_auto_20191126_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedsearch',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
