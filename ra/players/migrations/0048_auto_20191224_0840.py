# Generated by Django 2.2.5 on 2019-12-24 08:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0047_schoolsvisit_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='player',
            name='updated_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]