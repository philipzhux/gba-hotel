from django.db import models
from home.models import GuestDetails


class HotelProfile(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    email = models.CharField(max_length=250)
    contact_no = models.CharField(max_length=250)
    owner_name = models.CharField(max_length=250)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)


class RoomClass(models.Model):
    class_id = models.AutoField(primary_key=True)
    room_type = models.CharField(max_length=250)
    hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE)
    price_per_day = models.PositiveIntegerField(default=0)


class DiscountDetails(models.Model):
    discount_id = models.CharField(max_length=250, primary_key=True)
    #hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE)
    month_valid = models.CharField(max_length=4)
    min_nights = models.PositiveIntegerField(default=0)
    room_class = models.ForeignKey(RoomClass, to_field='class_id',on_delete=models.CASCADE)
    offer_percent = models.PositiveIntegerField(default=0)


class ReservationDetails(models.Model):
    BOOKING_STATUS = (('B', 'Booked'),('C1', 'Cancelled by user'),('C2', 'Cancelled by hotel'))
    reservation_id = models.AutoField(primary_key=True)
    reservation_status = models.CharField(max_length=2, choices=BOOKING_STATUS)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    check_in_time = models.CharField(max_length=15)
    check_out_time = models.CharField(max_length=15)
    guest = models.ForeignKey(GuestDetails, to_field='user_name',on_delete=models.CASCADE)
    hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE)
    # room = models.ForeignKey(RoomClass, to_field='class_id',on_delete=models.CASCADE)
    room_class =  models.ForeignKey(RoomClass, to_field='class_id',on_delete=models.CASCADE)
    discount = models.ForeignKey(DiscountDetails, to_field='discount_id',on_delete=models.CASCADE, null=True, blank= True)
    total_guests = models.PositiveIntegerField(default=0)
    total_days = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=0)
    reservation_date = models.DateField()


class RoomDetails(models.Model):
    #ROOM_STATUS = (('V', 'Vacant'),('D', 'Dirty'),('O', 'Occupied'),('B', 'Booked'))
    reservation = models.ForeignKey(ReservationDetails, to_field='reservation_id', null=True,on_delete=models.CASCADE,blank=True)
    room_key = models.AutoField(primary_key=True)
    room_no = models.PositiveIntegerField(null=True)
    # hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE)
    guest = models.ForeignKey(GuestDetails, to_field='user_name',on_delete=models.SET_NULL,null=True,blank=True)
    room_class = models.ForeignKey(RoomClass, to_field='class_id',on_delete=models.CASCADE)
    layout = models.CharField(max_length=40)
    floor_no = models.PositiveIntegerField(default=0)
    # room_status = models.CharField(max_length=1)
    # Need to change

class DiscountDistribution(models.Model):
    distribution_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(HotelProfile, to_field='hotel_id',on_delete=models.CASCADE)
    guest = models.ForeignKey(GuestDetails, to_field='user_name',on_delete=models.CASCADE)
    discount = models.ForeignKey(DiscountDetails, to_field='discount_id',on_delete=models.CASCADE)


