# Generated by Django 3.0.7 on 2021-04-09 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayScale',
            fields=[
                ('position', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('gross_pay', models.BigIntegerField()),
                ('net_pay', models.BigIntegerField()),
                ('basic_pay', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EmplyeeProfile',
            fields=[
                ('user_name', models.CharField(max_length=250, null=True)),
                ('email', models.CharField(max_length=250, null=True)),
                ('password', models.CharField(max_length=250, null=True)),
                ('country', models.CharField(max_length=250, null=True)),
                ('contact_no', models.CharField(max_length=25, null=True)),
                ('passport_no', models.CharField(max_length=30, null=True)),
                ('experience', models.IntegerField(default=0)),
                ('address', models.CharField(max_length=400, null=True)),
                ('employee_id', models.AutoField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=250, null=True)),
                ('state', models.CharField(max_length=250, null=True)),
                ('hotel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reservations.HotelProfile')),
                ('position', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='administration.PayScale')),
            ],
        ),
    ]
