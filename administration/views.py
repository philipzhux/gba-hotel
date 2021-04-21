from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from administration.models import EmplyeeProfile
from reservations.models import HotelProfile, ReservationDetails, RoomDetails
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist

def admin_login(request):
    if 'employee_id' in request.session:
        if request.session['position'] == 'admin':
            return redirect('admin')
        else:
            return redirect('employee')
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        try:
            if '@' in str(user_name):
                record = EmplyeeProfile.objects.get(email=user_name)
            else:
                record = EmplyeeProfile.objects.get(user_name=user_name)
        except ObjectDoesNotExist:
            return render(request, 'admin_login.html', {'message': 'Employee id does not exist.'})
        if password == record.password:
            request.session['employee_name'] = record.user_name
            request.session['employee_id'] = record.employee_id
            position = EmplyeeProfile.objects.get(pk=record.employee_id).position_id
            request.session['position'] = position
            request.session['hotel_id'] = record.hotel_id
            if position == 'admin':
                return redirect('admin')
            else:
                return redirect('employee')
        else:
            return render(request, 'admin_login.html', {'message': 'Password is incorrect'})
    return render(request, 'admin_login.html')


def admin_signup(request):
    if 'employee_name' in request.session:
        if request.session['position'] == 'admin':
            return redirect('admin')
        elif request.session['position'] == 'employee':
            return redirect('employee')
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        passport_no = request.POST.get('passport_no')

        try:
            record = EmplyeeProfile.objects.get(email=str(email))
            return render(request, 'admin_signup.html', {'message': 'Email already exists. Please login to continue'})
        except ObjectDoesNotExist:
            new_employee = EmplyeeProfile()
            new_employee.user_name = user_name
            new_employee.email = email
            new_employee.password = password
            new_employee.contact_no = phone_number
            new_employee.address = address
            new_employee.state = state
            new_employee.city = city
            new_employee.country = country
            new_employee.passport_no = passport_no
            new_employee.save()
            return redirect('admin_login')
    return render(request, 'admin_signup.html')


def admin(request):
    try:
        return render(request, 'admin.html', {'name': request.session['employee_name']})
    except:
        return redirect('admin_login')


def create_employee(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    if request.method == 'POST':
        position = request.POST.get('position')
        experience = request.POST.get('experience')
        hotel_id = EmplyeeProfile.objects.get(employee_id=request.session['employee_id']).hotel_id
        hotel_name = HotelProfile.objects.get(pk=hotel_id).name
        new_employee = EmplyeeProfile(position_id=position, experience=experience, hotel_id=hotel_id)
        new_employee.save()
        return render(request, 'create_employee.html', {'message': 'Employee created successfully.',
                                                        'hotel_id': hotel_id, 'hotel_name': hotel_name,
                                                        'name': request.session['employee_name']})
    hotel_name = HotelProfile.objects.get(pk=request.session['hotel_id']).name
    return render(request, 'create_employee.html', {'hotel_id': request.session['hotel_id'], 'hotel_name': hotel_name,
                                                    'name': request.session['employee_name']})


def update_employee(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    if request.is_ajax():
        print(request.GET.get('employee_id'))
        employee_id = request.GET.get('employee_id')
        try:
            record = EmplyeeProfile.objects.get(pk=employee_id)
            return JsonResponse({'message': 'success', 'position': record.position_id, 'experience': record.experience})
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'failure'})
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        employee = EmplyeeProfile.objects.get(pk=employee_id)
        employee.experience = request.POST.get('experience')
        employee.position_id = request.POST.get('position')
        employee.save()
        hotel_id = EmplyeeProfile.objects.get(employee_id=request.session['employee_id']).hotel_id
        hotel_name = HotelProfile.objects.get(pk=hotel_id).name
        return render(request, 'update_employee.html', {'name': request.session['employee_name'],
                                                        'message': 'Successfully updated.',
                                                        'hotel_id': hotel_id, 'hotel_name': hotel_name})
    hotel_name = HotelProfile.objects.get(pk=request.session['hotel_id']).name
    return render(request, 'update_employee.html', {'name': request.session['employee_name'],
                                                    'hotel_id': request.session['hotel_id'], 'hotel_name': hotel_name })


def employee(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    reservations = ReservationDetails.objects.filter(reservation_status='B')
    details = []
    for reservation in reservations:
        details.append((reservation, HotelProfile.objects.get(pk=reservation.hotel_id).name))
    return render(request, 'employee.html', {'name': request.session['employee_name'],
                                             'details': details})


def employee_profile(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    record = EmplyeeProfile.objects.get(pk=request.session['employee_id'])
    hotel_name = HotelProfile.objects.get(pk=record.hotel_id).name
    return render(request, 'employee_profile.html', {'name': request.session['employee_name'],
                                                     'employee': record, 'hotel_name':hotel_name})


def cancel_records(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    reservation_id = request.GET.get('reservation_id')
    record = ReservationDetails.objects.get(pk=reservation_id)
    record.reservation_status = 'C2'
    record.save()
    rooms = RoomDetails.objects.filter(reservation_id=reservation_id)
    for room in rooms:
        room.reservation_id = None
        room.save()
    return redirect('employee')


def reservation_records(request):
    if 'employee_name' not in request.session:
        return redirect('admin_login')
    confirmed_reservations = ReservationDetails.objects.filter(hotel_id=request.session['hotel_id']).filter(
        reservation_status='B')
    cancelled_reservations1 = ReservationDetails.objects.filter(hotel_id=request.session['hotel_id']).filter(
        reservation_status='C1')
    cancelled_reservations2 = ReservationDetails.objects.filter(hotel_id=request.session['hotel_id']).filter(
        reservation_status='C2')
    confirmed_details, cancelled_details1, cancelled_details2 = [], [], []
    for confirmed_reservation in confirmed_reservations:
        confirmed_details.append(confirmed_reservation)
    for cancelled_reservation1 in cancelled_reservations1:
        cancelled_details1.append(cancelled_reservation1)
    for cancelled_reservation2 in cancelled_reservations2:
        cancelled_details2.append(cancelled_reservation2)
    #hotel_name = HotelProfile.objects.get(pk=request.session['hotel_id']).name
    return render(request, 'reservation_records.html', {'name': request.session['employee_name'],
                                                    'confirmed_details': confirmed_details,
                                                    'cancelled_details1': cancelled_details1,
                                                    'cancelled_details2': cancelled_details2,
                                                    'hotel_name': "hotel_name"})





def office_logout(request):
    if 'employee_name' in request.session:
        request.session.clear()
        return redirect('admin_login')



