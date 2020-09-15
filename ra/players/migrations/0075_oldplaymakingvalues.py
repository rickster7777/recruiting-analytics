# Generated by Django 2.2.5 on 2020-05-19 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0074_player_web_highlighted_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldPlayMakingValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_sack_maxpreps', models.FloatField(blank=True, null=True)),
                ('old_interception_maxpreps', models.FloatField(blank=True, null=True)),
                ('old_touchdown_maxpreps', models.FloatField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.Player')),
            ],
        ),
    ]