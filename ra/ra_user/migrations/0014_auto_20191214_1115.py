# Generated by Django 2.2.5 on 2019-12-14 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ra_user', '0013_auto_20191210_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]