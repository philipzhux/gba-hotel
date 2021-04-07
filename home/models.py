from django.db import models
from django import forms


class GuestDetails(models.Model):
    user_name = models.CharField(primary_key=True, max_length=250)
    email = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    passport_no = models.CharField(max_length=20)
