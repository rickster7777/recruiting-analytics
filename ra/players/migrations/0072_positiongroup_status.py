# Generated by Django 2.2.5 on 2020-05-09 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0071_player_video_highlight_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='positiongroup',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='inactive', max_length=20),
        ),
    ]