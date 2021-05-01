# Generated by Django 3.0.7 on 2021-04-09 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GuestDetails',
            fields=[
                ('user_name', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=250)),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('password', models.CharField(max_length=250)),
                ('phone_number', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=400)),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('country', models.CharField(max_length=250)),
                ('passport_no', models.CharField(max_length=20)),
            ],
        ),
    ]