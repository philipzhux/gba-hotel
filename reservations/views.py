from django.shortcuts import render, redirect, reverse
from django.template import RequestContext
from django.db.models import Min
from reservations.models import ReservationDetails, RoomClass, RoomDetails, DiscountDetails, HotelProfile, DiscountDistribution, GuestDetails
from django.http import JsonResponse
import datetime
from django.core.mail import EmailMessage
from django.db import connection

def reservation(request):

    if 'username' not in request.session:
        return redirect('home')
    if request.is_ajax():
        behavior = request.GET.get('behavior')
        if behavior == "check_discount":
            room_type = request.GET.get('room_type')
            complete_id=request.GET.get('hotel_id')
            nights = request.GET.get('nights')
            hotel_id = int(complete_id[complete_id.index('-')+1:])
            class_id = RoomClass.objects.get(room_type=room_type,hotel=hotel_id).class_id
            records = DiscountDetails.objects.filter(room_class_id=class_id)
            for record in records:
                if(int(nights)>=record.min_nights):
                    return JsonResponse({'discount_id': record.discount_id, 'offer_percent': record.offer_percent,
                                            'message': 'success'})
            return JsonResponse({'message': 'none'})
        elif behavior == "select_room":
            room_type = request.GET.get('room_type')
            complete_id=request.GET.get('hotel_id')
            hotel_id = int(complete_id[complete_id.index('-')+1:])
            print("hotel_id:",hotel_id,"room_type:",room_type)
            with connection.cursor() as cursor:
                cursor.execute("SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s",[room_type,hotel_id])
                room_price = cursor.fetchone()[0]
            #room_price = RoomClass.objects.raw("(SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel = %s)",[room_type,hotel_id])[0]
            class_id = RoomClass.objects.get(room_type=room_type,hotel=hotel_id).class_id
            # --> raw("(SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel = %s)",[room_type,hotel_id])
            print("room_price:",room_price) 
            rooms_available = RoomDetails.objects.raw("SELECT * FROM reservations_roomdetails WHERE reservation_id NOT \
IN (SELECT reservation_id FROM reservations_reservationdetails WHERE check_in_date<=(select date('now')) \
AND check_out_date>(SELECT date('now'))) AND room_class_id IN (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s)"\
,[room_type,hotel_id])
            available_num = len(rooms_available)
            # Need to change 
            return JsonResponse({'room_price': room_price, 'rooms_available': available_num})


    if request.method == 'POST':
        new_reservation = ReservationDetails()
        new_reservation.guest_id = request.session['user_id']
        new_reservation.reservation_status = "B" 
        new_reservation.check_in_date = datetime.datetime.strptime(request.POST.get('check_in_date'), "%Y-%m-%d")
        new_reservation.check_in_time = request.POST.get('check_in_time')+request.POST.get('session1')
        new_reservation.check_out_date = datetime.datetime.strptime(request.POST.get('check_out_date'), "%Y-%m-%d")
        new_reservation.check_out_time = request.POST.get('check_out_time')+request.POST.get('session2')
        new_reservation.total_guests = request.POST.get('total_guests')
        new_reservation.total_days = request.POST.get('total_days')
        new_reservation.total_rooms = request.POST.get('total_rooms')
        new_reservation.discounted_price = float(request.POST.get('discounted_price'))
        new_reservation.total_cost = float(request.POST.get('total_cost'))
        new_reservation.reservation_date = datetime.datetime.today()
        try:
            int(request.POST.get('discount_id'))
            new_reservation.discount_id = int(request.POST.get('discount_id'))
        except:
            pass
        complete_id = request.POST.get('hotel_id')
        new_reservation.hotel_id = int(complete_id[complete_id.index('-')+1:])
        new_reservation.room_class_id = RoomClass.objects.get(room_type=request.POST.get('room_type'),hotel=new_reservation.hotel_id).class_id
        new_reservation.save()
        # update room details
        rooms = RoomDetails.objects.filter(room_class_id=new_reservation.room_class_id).order_by('room_no') [:int(new_reservation.total_rooms)]
        for room in rooms:
            room.guest_id = new_reservation.guest_id
            room.reservation_id = new_reservation.reservation_id
            room.save()
        if(new_reservation.discount_id):
            discount_availed = DiscountDistribution(discount_id=new_reservation.discount_id, guest_id=new_reservation.guest_id,
                                            hotel_id=new_reservation.hotel_id)
            discount_availed.save()
        return redirect(reverse('summary') + '?reservation_id={}'.format(new_reservation.reservation_id))
    hotel_id = request.GET.get('hotel_id')
    hotel_name = HotelProfile.objects.get(pk=hotel_id).name
    records = RoomClass.objects.filter(hotel_id=hotel_id)
    room_types = [records[i].room_type for i in range(len(records))]
    return render(request, 'new_reservation.html', {'name': request.session['username'], 'room_types': room_types,
                                                'hotel_id': "hid-"+str(hotel_id), 'hotel_name': hotel_name}
                  )


def find_hotel(request):
    if 'username' not in request.session:
        return redirect('login')
    if request.is_ajax():
        city = request.GET.get('city')
        if(city=="none"):
            hotels = HotelProfile.objects.all()
        hotels = HotelProfile.objects.filter(city=city)
        hotels_list = []
        for hotel in hotels:
            min_price = RoomClass.objects.filter(hotel_id=hotel.hotel_id).aggregate(Min('price_per_day'))['price_per_day__min']
            hotels_list.append((hotel.hotel_id, hotel.name, min_price))
        return JsonResponse({'hotels_list': hotels_list})

    return render(request, 'search.html', {'name': request.session['username']})


def summary(request):
    if 'username' not in request.session:
        return redirect('login')
    reservation_id = request.GET.get('reservation_id')
    new_reservation = ReservationDetails.objects.get(pk=reservation_id)
    hotel = HotelProfile.objects.get(pk=new_reservation.hotel_id)
    return render(request, 'summary.html', {'name': request.session['username'], 'new_reservation' :new_reservation,
                                            'hotel': hotel})


def cancel_reservation(request):
    if 'username' not in request.session:
        return redirect('login')
    reservation_id = request.GET.get('reservation_id')
    record = ReservationDetails.objects.get(pk=reservation_id)
    record.reservation_status = 'C1'
    record.save()
    rooms = RoomDetails.objects.filter(reservation_id=reservation_id)
    for room in rooms:
        #room.room_status = 'V'
        room.reservation_id = None
        room.guest_id = None
        room.save()
    return redirect('dashboard')
