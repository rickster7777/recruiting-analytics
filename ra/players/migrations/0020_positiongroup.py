# Generated by Django 2.2.5 on 2019-11-09 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0019_player_rank'),
    ]

    operations = [
        migrations.CreateModel(
            name='PositionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]