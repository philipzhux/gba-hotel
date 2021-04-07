from django.shortcuts import render, redirect, reverse
from django.template import RequestContext
from django.db.models import Min
from reservations.models import ReservationDetails, RoomPriceDetails, RoomDetails, DiscountDetails, HotelProfile, DiscountAvailed, GuestDetails
from django.http import JsonResponse
import datetime
from django.core.mail import EmailMessage


def reservation(request):

    if 'username' not in request.session:
        return redirect('home')
    if request.is_ajax():
        request_no = request.GET.get('request_no')
        if int(request_no) == 1:
            room_type = request.GET.get('room_type')
            room_price = RoomPriceDetails.objects.get(room_type=room_type).price_per_day
            rooms_available = len(RoomDetails.objects.filter(room_id=room_type).filter(room_status='V'))
            return JsonResponse({'room_price': room_price, 'rooms_available': rooms_available})
        elif int(request_no) == 2:
            room_type = request.GET.get('room_type')
            no_of_days = request.GET.get('no_of_days')
            records = DiscountDetails.objects.filter(room_id=room_type)
            for record in records:
                low, high = map(int, record.length_of_stay.split(':'))
                if str(high).strip() != '-1':
                    if low < int(no_of_days) <= high:
                        return JsonResponse({'discount_id': record.discount_id, 'offer_percent': record.offer_percent,
                                             'message': 'success'})
                elif str(high).strip() == '-1':
                    if int(no_of_days) > low:
                        return JsonResponse({'discount_id': record.discount_id, 'offer_percent': record.offer_percent,
                                             'message': 'success'})
            return JsonResponse({'message': 'none'})

    if request.method == 'POST':
        new_reservation = ReservationDetails()
        new_reservation.guest_id = request.session['user_id']
        new_reservation.reservation_status = "B"
        new_reservation.check_in_date = request.POST.get('check_in_date')
        new_reservation.check_in_time = request.POST.get('check_in_time')+request.POST.get('session1')
        new_reservation.check_out_date = request.POST.get('check_out_date')
        new_reservation.check_out_time = request.POST.get('check_out_time')+request.POST.get('session2')
        new_reservation.total_guests = request.POST.get('total_guests')
        new_reservation.total_days = request.POST.get('total_days')
        new_reservation.total_rooms = request.POST.get('total_rooms')
        new_reservation.discounted_price = float(request.POST.get('discounted_price'))
        new_reservation.total_cost = float(request.POST.get('total_cost'))
        new_reservation.reservation_date = datetime.datetime.today().strftime('%Y-%m-%d')
        try:
            int(request.POST.get('discount_id'))
            new_reservation.discount_id = int(request.POST.get('discount_id'))
        except:
            pass
        complete_id = request.POST.get('hotel_id')
        new_reservation.hotel_id = int(complete_id[complete_id.index('-')+1:])
        new_reservation.room_id = request.POST.get('room_type')
        new_reservation.save()
        # update room details
        rooms = RoomDetails.objects.filter(room_id=new_reservation.room_id).order_by('room_no') [:int(new_reservation.total_rooms)]
        for room in rooms:
            room.guest_id = new_reservation.guest_id
            room.room_status = 'B'
            room.reservation_id = new_reservation.reservation_id
            room.save()
        # update availed discount details
        if(new_reservation.discount_id):
            discount_availed = DiscountAvailed(discount_id=new_reservation.discount_id, guest_id=new_reservation.guest_id,
                                            hotel_id=new_reservation.hotel_id)
            discount_availed.save()
        # send email confirmation
        return redirect(reverse('summary') + '?reservation_id={}'.format(new_reservation.reservation_id))
    hotel_id = request.GET.get('hotel_id')
    hotel_name = HotelProfile.objects.get(pk=hotel_id).name
    records = RoomPriceDetails.objects.filter(hotel_id=hotel_id)
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
            min_price = RoomPriceDetails.objects.filter(hotel_id=hotel.hotel_id).aggregate(Min('price_per_day'))['price_per_day__min']
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
        room.room_status = 'V'
        room.reservation_id = None
        room.guest_id = None
        room.save()
    return redirect('dashboard')
