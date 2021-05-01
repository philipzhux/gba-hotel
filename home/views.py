from django.shortcuts import render, get_object_or_404, redirect
from .models import GuestDetails
from reservations.models import ReservationDetails, HotelProfile
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

def home(request):
    if 'username' in request.session:
        return render(request, 'home.html', {'name': request.session['username']})
    return render(request, 'home.html')


def login(request):
    if 'username' in request.session:
        return redirect('home')
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        if '@' in str(user_name):
            record = get_object_or_404(GuestDetails, email=user_name)
        else:
            record = get_object_or_404(GuestDetails, user_name=user_name)
        if password == record.password:
            request.session['username'] = record.first_name+" "+record.last_name
            request.session['user_id'] = record.user_name
            return redirect('home')
        else:
            return render(request, 'login.html', {'message': 'User id or password is incorrect'})
    return render(request, 'login.html')


def signup(request):
    if 'username' in request.session:
        return redirect('home')
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        passport_no = request.POST.get('passport_no')
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(email) FROM home_guestdetails WHERE email = %s",[str(email)])
            num = cursor.fetchone()[0]
            if(num):
                return render(request, 'signup.html', {'message': 'Email already exists. Please login to continue'})
            cursor.execute("INSERT INTO home_guestdetails(user_name,email,first_name,last_name,password,phone_number,address,state,city,country,passport_no)\
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[user_name,email,first_name,last_name,password,phone_number,address,state,city,country,passport_no])
        return redirect('home')
    return render(request, 'signup.html')


def logout(request):
    if 'username' in request.session:
        del request.session['username']
        return redirect('home')


def dashboard(request):
    if 'username' in request.session:
        print(request.session['user_id'])
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM reservations_reservationdetails WHERE guest_id = %s AND reservation_status='B'",[request.session['user_id']])
            reservations = dictfetchall(cursor)
            details = []
            #print(reservations)
            for reservation in reservations:
                cursor.execute("SELECT name from reservations_hotelprofile WHERE hotel_id = %s",[reservation["hotel_id"]])
                hotel_name = cursor.fetchone()[0]
                details.append((reservation, hotel_name))
        return render(request, 'dashboard.html', {'name': request.session['username'],
                                                  'details': details})
    else:
        return redirect('home')


def profile(request):
    if 'username' in request.session:
        record = get_object_or_404(GuestDetails, user_name=request.session['user_id'])
        return render(request, 'profile.html', {'name': request.session['username'], 'record': record})
    else:
        return redirect('home')


def reservation_history(request):
    if 'username' in request.session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM reservations_reservationdetails WHERE guest_id = %s AND reservation_status=%s",[request.session['user_id'],'B'])
            confirmed_reservations = dictfetchall(cursor)
            cursor.execute("SELECT * FROM reservations_reservationdetails WHERE guest_id = %s AND reservation_status=%s",[request.session['user_id'],'C1'])
            cancelled_reservations = dictfetchall(cursor)
            confirmed_details, cancelled_details = [], []
            for confirmed_reservation in confirmed_reservations:
                cursor.execute("SELECT name FROM reservations_hotelprofile WHERE hotel_id = %s",[confirmed_reservation['hotel_id']])
                confirmed_details.append((confirmed_reservation, cursor.fetchone()[0]))
            for cancelled_reservation in cancelled_reservations:
                cursor.execute("SELECT name FROM reservations_hotelprofile WHERE hotel_id = %s",[cancelled_reservation['hotel_id']])
                cancelled_details.append((cancelled_reservation, cursor.fetchone()[0]))=
        return render(request, 'reservation_history.html', {'name': request.session['username'],
                                                        'confirmed_details': confirmed_details,
                                                        'cancelled_details': cancelled_details})
    else:
        return redirect('home')


