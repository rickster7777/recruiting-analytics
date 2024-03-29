# Generated by Django 2.2.5 on 2019-11-08 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ra_user', '0008_user_welcome_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=150, unique=True)),
                ('subscription_id', models.CharField(max_length=150)),
                ('plan', models.CharField(default='monthly', max_length=50)),
                ('status', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='subscription',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ra_user.UserSubscription'),
        ),
    ]
