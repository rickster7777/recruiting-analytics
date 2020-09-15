# Generated by Django 2.2.5 on 2019-10-21 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0004_school_address'),
        ('ra_user', '0005_delete_schoolinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='coach_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.School'),
        ),
        migrations.AddField(
            model_name='user',
            name='privacy_and_policy',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='school_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]