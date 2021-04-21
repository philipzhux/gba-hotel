from django.db import models
from reservations.models import HotelProfile




class PayScale(models.Model):
    position = models.CharField(max_length=250, primary_key=True)
    gross_pay = models.BigIntegerField()
    net_pay = models.BigIntegerField()
    basic_pay = models.BigIntegerField()


class EmplyeeProfile(models.Model):
    user_name = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=250, null=True)
    password = models.CharField(max_length=250, null=True)
    position = models.ForeignKey(PayScale, to_field='position',on_delete=models.CASCADE,null=True)
    country = models.CharField(max_length=250, null=True)
    contact_no = models.CharField(max_length=25, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    experience = models.IntegerField(default=0)
    address = models.CharField(max_length=400, null=True)
    employee_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE,null=True)
    city = models.CharField(max_length=250, null=True)
    state = models.CharField(max_length=250, null=True)



