from django.db import connection
from django.http import HttpResponse
import csv
def a(request):
    filename ="/Users/philip/Downloads/4.23_21_17_data/request_guset_x6.csv"
    with open(filename, 'r') as data:
        a=csv.DictReader(data)
        for d in a:
            room_class = d['room_class_id']
            hotel = d['hotel_id']
            guest = d['guest_id']
            nights = d['total_days']
            ci_date = d['check_in_date']
            co_date = d['check_out_date']
            date = d['reservation_date']
            ci_time = d['check_in_time']
            co_time = d['check_out_time']
            roomnum = d['total_rooms']
            guestnum = d['total_guests']    
            with connection.cursor() as cursor:
                cursor.execute("SELECT price_per_day FROM reservations_roomclass WHERE class_id = %s",[room_class])
                room_price = cursor.fetchone()[0]
                total_cost = float(room_price)*float(roomnum)*float(nights)
                cursor.execute("INSERT INTO reservations_reservationdetails(guest_id,reservation_status,check_in_date,"\
                "check_in_time,check_out_date,check_out_time,total_guests,total_days,total_rooms,discounted_price,total_cost,reservation_date,"\
                "hotel_id) VALUES (%s,'B',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[guest,ci_date,ci_time,co_date,co_time,guestnum,nights,roomnum,total_cost,total_cost,date,hotel])
                cursor.execute("SELECT last_insert_rowid()")
                reservation_id = cursor.fetchone()[0]
                cursor.execute('''SELECT room_key FROM reservations_roomdetails WHERE room_class_id = %s
                AND room_key NOT IN 
                (SELECT room_key_id FROM reservations_reservationroom WHERE reservation_id
                IN (SELECT reservation_id FROM reservations_reservationdetails WHERE (%s<=check_in_date AND check_in_date<%s)
                OR (%s<check_out_date AND check_out_date<=%s) OR (check_in_date<=%s AND %s<check_out_date))) LIMIT %s
                '''
                ,[room_class,ci_date,co_date,ci_date,co_date,ci_date,ci_date,roomnum])
                rooms = cursor.fetchall()
                for room in rooms:
                    key = room[0]
                    cursor.execute("INSERT INTO reservations_reservationroom(reservation_id,room_key_id) VALUES (%s,%s)",[reservation_id,key])

    return HttpResponse("Success.")