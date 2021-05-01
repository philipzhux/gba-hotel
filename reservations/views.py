from django.shortcuts import render, redirect, reverse
from django.template import RequestContext
from django.db.models import Min
from reservations.models import ReservationDetails, RoomClass, RoomDetails, DiscountDetails, HotelProfile, DiscountDistribution, GuestDetails
from django.http import JsonResponse
import datetime
from django.core.mail import EmailMessage
from django.db import connection
import django.contrib.staticfiles
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))
    

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
            with connection.cursor() as cursor:
                # cursor.execute("SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel = %s")
                # class_id = cursor.fetchone()[0]
                cursor.execute("SELECT * FROM reservations_discountdetails WHERE room_class_id in (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s)"\
                ,[room_type,hotel_id])
                records = dictfetchall(cursor)

            
            # class_id = RoomClass.objects.get(room_type=room_type,hotel=hotel_id).class_id
            # records = DiscountDetails.objects.filter(room_class_id=class_id)
            for record in records:
                if(int(nights)>=record['min_nights']):
                    return JsonResponse({'discount_id': record["discount_id"], 'offer_percent': record["offer_percent"],
                                            'message': 'success'})
            return JsonResponse({'message': 'none'})
        elif behavior == "select_room":
            room_type = request.GET.get('room_type')
            complete_id=request.GET.get('hotel_id')
            ci_date = request.GET.get('cid')
            co_date = request.GET.get('cod')
            hotel_id = int(complete_id[complete_id.index('-')+1:])
            print("hotel_id:",hotel_id,"room_type:",room_type)
            with connection.cursor() as cursor:
                cursor.execute("SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s",[room_type,hotel_id])
                room_price = cursor.fetchone()[0]
                #room_price = RoomClass.objects.raw("(SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel = %s)",[room_type,hotel_id])[0]
                # class_id = RoomClass.objects.get(room_type=room_type,hotel=hotel_id).class_id
                # cursor.execute("SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s",[room_type,hotel_id])
                # class_id = cursor.fetchone()[0]
                cursor.execute('''
                SELECT COUNT(room_key) FROM 
                (SELECT room_key FROM reservations_roomdetails WHERE room_class_id IN
                (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s)
                AND room_key NOT IN 
                (SELECT room_key_id FROM reservations_reservationroom WHERE reservation_id
                IN (SELECT reservation_id FROM reservations_reservationdetails WHERE (%s<=check_in_date AND check_in_date<%s)
                OR (%s<check_out_date AND check_out_date<=%s) OR (check_in_date<=%s AND %s<check_out_date))))
                '''
                ,[room_type,hotel_id,ci_date,co_date,ci_date,co_date,ci_date,ci_date])
                available_num = cursor.fetchone()[0]
                # cursor.execute('''
                # SELECT reservation_id FROM reservations_reservationdetails WHERE %s<=check_in_date
                # AND check_in_date<%s
                # '''
                # ,[ci_date,co_date])
                # print(dictfetchall(cursor))

            # --> raw("(SELECT price_per_day FROM reservations_roomclass WHERE room_type = %s AND hotel = %s)",[room_type,hotel_id])
            print("room_price:",room_price) 
            # rooms_available = RoomDetails.objects.raw("SELECT * FROM reservations_roomdetails WHERE reservation_id IS NULL OR reservation_id NOT "\
            # "IN (SELECT reservation_id FROM reservations_reservationdetails WHERE %s<=check_in_date<%s "\
            # "OR %s<check_out_date<=%s OR check_in_date<=%s<check_out_date AND room_class_id IN (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s))"\
            # ,[ci_date,co_date,ci_date,co_date,ci_date,room_type,hotel_id])
            # available_num = len(rooms_available)
            # Need to change 
            return JsonResponse({'room_price': room_price, 'rooms_available': available_num})


    if request.method == 'POST':
        room_type=request.POST.get('room_type')
        complete_id = request.POST.get('hotel_id')
        nights = request.GET.get('nights')
        ci_date = request.POST.get('check_in_date')
        co_date = request.POST.get('check_out_date')
        hotel_id = int(complete_id[complete_id.index('-')+1:])
        with connection.cursor() as cursor:
                #cursor.execute("SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s",[room_type,hotel_id])
                #class_id = cursor.fetchone()[0]
                if len(request.POST.get('discount_id')) and request.POST.get('discount_id')!='N/A':
                    print(request.POST.get('discount_id'))
                    cursor.execute("INSERT INTO reservations_reservationdetails(guest_id,reservation_status,check_in_date,"\
                    "check_in_time,check_out_date,check_out_time,total_guests,total_days,total_rooms,discounted_price,total_cost,reservation_date,"\
                    "discount_id,hotel_id) VALUES (%s,'B',%s,%s,%s,%s,%s,%s,%s,%s,%s,date('now'),%s,%s)",\
                    [request.session['user_id'],request.POST.get('check_in_date'),request.POST.get('check_in_time')+request.POST.get('session1'),\
                    request.POST.get('check_out_date'),request.POST.get('check_out_time')+request.POST.get('session2'),request.POST.get('total_guests'),\
                    request.POST.get('nights'),request.POST.get('total_rooms'),float(request.POST.get('discounted_price')),float(request.POST.get('total_cost')),\
                    request.POST.get('discount_id'),hotel_id])
                else:
                    cursor.execute("INSERT INTO reservations_reservationdetails(guest_id,reservation_status,check_in_date,"\
                    "check_in_time,check_out_date,check_out_time,total_guests,total_days,total_rooms,discounted_price,total_cost,reservation_date,"\
                    "hotel_id) VALUES (%s,'B',%s,%s,%s,%s,%s,%s,%s,%s,%s,date('now'),%s)",\
                    [request.session['user_id'],request.POST.get('check_in_date'),request.POST.get('check_in_time')+request.POST.get('session1'),\
                    request.POST.get('check_out_date'),request.POST.get('check_out_time')+request.POST.get('session2'),request.POST.get('total_guests'),\
                    request.POST.get('nights'),request.POST.get('total_rooms'),float(request.POST.get('discounted_price')),float(request.POST.get('total_cost')),\
                    hotel_id])
                cursor.execute("SELECT last_insert_rowid()")
                reservation_id = cursor.fetchone()[0]
                cursor.execute('''SELECT room_key FROM reservations_roomdetails WHERE room_class_id IN
                (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s)
                AND room_key NOT IN 
                (SELECT room_key_id FROM reservations_reservationroom WHERE reservation_id
                IN (SELECT reservation_id FROM reservations_reservationdetails WHERE (%s<=check_in_date AND check_in_date<%s)
                OR (%s<check_out_date AND check_out_date<=%s) OR (check_in_date<=%s AND %s<check_out_date))) LIMIT %s
                '''
                ,[room_type,hotel_id,ci_date,co_date,ci_date,co_date,ci_date,ci_date,int(request.POST.get('total_rooms'))])
            #     cursor.execute("SELECT room_key FROM reservations_roomdetails WHERE room_key IN (SELECT room_key FROM "\
            #     "reservations_roomdetails WHERE reservation_id IS NULL OR reservation_id NOT "\
            # "IN (SELECT reservation_id FROM reservations_reservationdetails WHERE %s<=check_in_date<%s "\
            # "OR %s<check_out_date<=%s OR check_in_date<=%s<check_out_date AND room_class_id IN (SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s)) LIMIT %s)",\
            #     [reservation_id,ci_date,co_date,ci_date,co_date,ci_date,room_type,hotel_id,int(request.POST.get('total_rooms'))])
                rooms = cursor.fetchall()
                for room in rooms:
                    key = room[0]
                    cursor.execute("INSERT INTO reservations_reservationroom(reservation_id,room_key_id) VALUES (%s,%s)",[reservation_id,key])
                    
                if len(request.POST.get('discount_id')) and request.POST.get('discount_id')!='N/A':
                    cursor.execute("INSERT INTO reservations_discountdistribution(discount_id,guest_id,hotel_id) VALUES (%s,%s,%s)",[request.POST.get('discount_id'),request.session['user_id'],hotel_id])
                    # discount_availed = DiscountDistribution(discount_id=new_reservation.discount_id, guest_id=new_reservation.guest_id,
                    #                                 hotel_id=new_reservation.hotel_id)
                    # discount_availed.save()
        # new_reservation = ReservationDetails()
        # new_reservation.guest_id = request.session['user_id']
        # new_reservation.reservation_status = "B" 
        # new_reservation.check_in_date = datetime.datetime.strptime(request.POST.get('check_in_date'), "%Y-%m-%d")
        # new_reservation.check_in_time = request.POST.get('check_in_time')+request.POST.get('session1')
        # new_reservation.check_out_date = datetime.datetime.strptime(request.POST.get('check_out_date'), "%Y-%m-%d")
        # new_reservation.check_out_time = request.POST.get('check_out_time')+request.POST.get('session2')
        # new_reservation.total_guests = request.POST.get('total_guests')
        # new_reservation.total_days = request.POST.get('total_days')
        # new_reservation.total_rooms = request.POST.get('total_rooms')
        # new_reservation.discounted_price = float(request.POST.get('discounted_price'))
        # new_reservation.total_cost = float(request.POST.get('total_cost'))
        # new_reservation.reservation_date = datetime.datetime.today()
        # try:
        #     with connection.cursor() as cursor:
        #         cursor.execute("UPDATE reservations_reservationdetails SET discount_id = %s",[request.POST.get('discount_id')]))
        #     #new_reservation.discount_id = int(request.POST.get('discount_id'))
        # except:
        #     pass
        # complete_id = request.POST.get('hotel_id')
        # with connection.cursor() as cursor:
        #     cursor.execute("SELECT class_id FROM reservations_roomclass WHERE room_type = %s AND hotel_id = %s",[room_type,hotel_id])
        #     class_id = cursor.fetchone()[0]
        #     cursor.execute("UPDATE reservations_reservationdetails SET room_class_id = %d WHERE "%class_id)
        #     cursor.execute("UPDATE reservations_reservationdetails SET hotel_id = %d WHERE "%int(complete_id[complete_id.index('-')+1:]))
        
        #new_reservation.hotel_id = int(complete_id[complete_id.index('-')+1:])
        #new_reservation.room_class_id = RoomClass.objects.get(room_type=request.POST.get('room_type'),hotel=new_reservation.hotel_id).class_id
        #new_reservation.save()
        
        # update room details

        # rooms = RoomDetails.objects.filter(room_class_id=new_reservation.room_class_id).order_by('room_no') [:int(new_reservation.total_rooms)]

        # for room in rooms:
        #     room.guest_id = new_reservation.guest_id
        #     room.reservation_id = new_reservation.reservation_id
        #     room.save()

        return redirect(reverse('summary') + '?reservation_id={}'.format(reservation_id))
    hotel_id = request.GET.get('hotel_id')
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM reservations_hotelprofile WHERE hotel_id=%s",[hotel_id])
        hotel_name = cursor.fetchone()[0]
        cursor.execute("SELECT room_type FROM reservations_roomclass WHERE hotel_id=%s",[hotel_id])
        records = cursor.fetchall()
    # hotel_name = HotelProfile.objects.get(pk=hotel_id).name
    # records = RoomClass.objects.filter(hotel_id=hotel_id)
    room_types = [records[i][0] for i in range(len(records))]
    return render(request, 'new_reservation.html', {'name': request.session['username'], 'room_types': room_types,
                                                'hotel_id': "hid-"+str(hotel_id), 'hotel_name': hotel_name}
                  )


def find_hotel(request):
    if 'username' not in request.session:
        return redirect('login')
    if request.is_ajax():
        city = request.GET.get('city')
        print(city)
        hotels = HotelProfile.objects.raw("SELECT * FROM reservations_hotelprofile WHERE city=%s",[city])
        hotels_list = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM reservations_hotelprofile WHERE city=%s",[city])
            hotels = dictfetchall(cursor)
            for hotel in hotels:
                cursor.execute("SELECT MIN(price_per_day) FROM reservations_roomclass WHERE hotel_id = %s",[hotel["hotel_id"]])
                min_price = cursor.fetchone()[0]
                #min_price = RoomClass.objects.filter(hotel_id=hotel.hotel_id).aggregate(Min('price_per_day'))['price_per_day__min']
                hotels_list.append((hotel['hotel_id'], hotel['name'], min_price))
        return JsonResponse({'hotels_list': hotels_list})

    return render(request, 'search.html', {'name': request.session['username']})


def summary(request):
    if 'username' not in request.session:
        return redirect('login')
    reservation_id = request.GET.get('reservation_id')
    #new_reservation = ReservationDetails.objects.raw("SELECT * FROM reservations_reservationdetails WHERE reservation_id = %s",[reservation_id])
    #new_reservation = ReservationDetails.objects.get(pk=reservation_id)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM reservations_hotelprofile WHERE hotel_id IN (SELECT hotel_id FROM reservations_reservationdetails WHERE reservation_id = %s)",[reservation_id])
        hotel = dictfetchone(cursor)
        cursor.execute("SELECT * FROM reservations_reservationdetails WHERE reservation_id = %s",[reservation_id])
        new_reservation = dictfetchone(cursor)
        cursor.execute('''SELECT room_class_id FROM reservations_roomdetails WHERE room_key IN 
        (SELECT room_key_id FROM reservations_reservationroom WHERE reservation_id = %s) LIMIT 1
        ''',[reservation_id])
        new_reservation['room_class_id'] = cursor.fetchone()[0]
    return render(request, 'summary.html', {'name': request.session['username'], 'new_reservation' :new_reservation,
                                            'hotel': hotel})


def cancel_reservation(request):
    if 'username' not in request.session:
        return redirect('login')
    reservation_id = request.GET.get('reservation_id')
    with connection.cursor() as cursor:
        cursor.execute("UPDATE reservations_reservationdetails SET reservation_status = 'C1' WHERE reservation_id = %s",[reservation_id])
        cursor.execute("DELETE FROM reservations_reservationroom WHERE reservation_id = %s ",[reservation_id])
    # record = ReservationDetails.objects.get(pk=reservation_id)
    # record.reservation_status = 'C1'
    # record.save()
    # rooms = RoomDetails.objects.filter(reservation_id=reservation_id)
    # for room in rooms:
    #     #room.room_status = 'V'
    #     room.reservation_id = None
    #     room.guest_id = None
    #     room.save()
    return redirect('dashboard')
