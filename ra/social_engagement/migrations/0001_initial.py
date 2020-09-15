# Generated by Django 2.2.5 on 2019-12-21 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SocialEngagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_handle', models.CharField(blank=True, max_length=250, null=True)),
                ('followers', models.CharField(blank=True, max_length=16, null=True)),
                ('following', models.CharField(blank=True, max_length=16, null=True)),
                ('new_followers', models.CharField(blank=True, max_length=16, null=True)),
                ('key_people_followers', models.CharField(blank=True, max_length=16, null=True)),
                ('key_people_followings', models.CharField(blank=True, max_length=16, null=True)),
                ('tweets', models.CharField(blank=True, max_length=16, null=True)),
                ('retweets', models.CharField(blank=True, max_length=16, null=True)),
                ('newly_followed', models.CharField(blank=True, max_length=16, null=True)),
            ],
        ),
    ]