from django.db import models
from reservations.models import HotelProfile




class PayScale(models.Model):
    designation = models.CharField(max_length=250, primary_key=True)
    MA = models.BigIntegerField()
    PF = models.BigIntegerField()
    gross_pay = models.BigIntegerField()
    net_pay = models.BigIntegerField()
    basic_pay = models.BigIntegerField()
    HRA = models.BigIntegerField()
    TA = models.BigIntegerField()


class EmplyeeProfile(models.Model):
    user_name = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=250, null=True)
    password = models.CharField(max_length=250, null=True)
    designation = models.ForeignKey(PayScale, to_field='designation',on_delete=models.CASCADE,null=True)
    country = models.CharField(max_length=250, null=True)
    contact_no = models.CharField(max_length=25, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    experience = models.IntegerField(default=0)
    address = models.CharField(max_length=400, null=True)
    employee_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE,null=True)
    city = models.CharField(max_length=250, null=True)
    state = models.CharField(max_length=250, null=True)


class SelfAddProfile(models.Model):
    increment_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmplyeeProfile, to_field='employee_id',on_delete=models.CASCADE)



