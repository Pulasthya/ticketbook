import json
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from sql_utils.utils import get_session
from tables.tables import *

session_customerID = None

def sign_up():

    content_type = request.headers.get('Content-Type')
    if (content_type == "application/json"):
        data = request.get_json()
        if "name" not in data or "password" not in data or "phone_number" not in data or "age" not in data:
            return "Incorrect or no data provided"
        new_customer = Customer(data["name"], data["phone_number"], data["age"], generate_password_hash(data["password"], method='sha256'))
        session = get_session()
        session.add(new_customer)
        session.commit()
        session.close()
        return f"Account for user {data['name']} has been created successful"
    return "Mis-Match in Content-Type"

def login():

    content_type = request.headers.get('Content-Type')
    if (content_type == "application/json"):
        data = request.get_json()
        if "phone_number" not in data or "password" not in data:
            return "Incorrect or no data provided"
        session = get_session()
        customer_qry_result = session.query(Customer).filter(Customer.phone_number == data["phone_number"])
        if not customer_qry_result:
            return f"User {data['phone_number']} does not exist"
        user = customer_qry_result[0]
        if not (check_password_hash(user.password, data["password"])):
            return "Invalid credentials passed"
        
        global session_customerID
        session_customerID = user.id
        session.close()
        return f"Successfully logged in {user.name}"
    return "Mis-Match in Content-Type"

def logout():
    global session_customerID
    if not session_customerID:
        return "No account is logged in"
    session_customerID = None
    return "Successfully logged out"

def get_movies():
    
    if not session_customerID:
        return "Login to continue"
    session = get_session()
    # print("Here mate")
    qry_results = session.query(Movie).all()
    session.close()
    # print(qry_results)
    movies = {}
    for result in qry_results:
        # movies.append({"Name": result.movie_name, "Release Date": result.release_date, "Duration":f"{result.duration} mins", "Director": {result.director}})
        movies[result.id] = {"Name": result.movie_name, "Release Date": str(result.release_date), "Duration":f"{result.duration} mins", "Director": result.director}
    # print(movies)
    return movies

def get_screening():

    # print("Here at screening")
    if not session_customerID:
        return "Login to continue"
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        data = request.get_json()
        if "movie_id" not in data or not data:
            return "Incorrect or no data provided"
        movie_id = data["movie_id"]
        session = get_session()
        qry_result = session.query(Screening).filter(Screening.movie_id == movie_id).all()
        # print(qry_result)
        if not qry_result:
            return "Sorry, currently no screenings"
        screenings = {}
        for result in qry_result:
            # print(type(result.id), type(result.auditorium.name), type(result.movie.movie_name), type(result.date), type(result.start_time))
            screenings[result.id] = {"Auditorium":result.auditorium.name, "Movie Name":result.movie.movie_name, "Date":str(result.date), "Start-Time": str(result.start_time)}
        # print(type(screenings), screenings)
        session.close()
        return json.dumps(screenings)
    return "Mis-Match in Content-Type"

def make_reservation():

    if not session_customerID:
        return "Login to continue"
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        data = request.get_json()
        if "screening_id" not in data or "num_seats" not in data or not data:
            return "Incorrect or no data provided"
        
        request_screening_id = data["screening_id"]
        request_num_seats = data["num_seats"]
        
        session = get_session()
        screening_qry_result = session.query(Screening).filter(Screening.id == request_screening_id).all()
        if not screening_qry_result:
            return "Enter a valid screening id"
        screening_qry_result = screening_qry_result[0]
        # print(type(screening_qry_result))
        # print(screening_qry_result)
        if screening_qry_result.seats_available == 0:
            return "All seats are booked"
        # print(screening_qry_result.seats_available, request_num_seats)
        if request_num_seats < 1 or screening_qry_result.seats_available < request_num_seats:
            # print("hererererere")
            return "Please request for a valid number of seats"
        reserve = Reservation(request_num_seats)
        loggedin_customer = session.query(Customer).filter(Customer.id == session_customerID).all()[0]
        # print(loggedin_customer)
        reserve.customer = loggedin_customer
        reserve.screening = screening_qry_result
        seat_row = screening_qry_result.seat_row_available
        seat_col = screening_qry_result.seat_col_available
        seats_booked = []
        for i in range(request_num_seats):
            # print(seat_row, seat_col)
            seats_booked.append([seat_row, seat_col])
            seat_reserve = Reservation_Seating()
            seat_qry_result = session.query(Seat).filter(Seat.audi_id == screening_qry_result.audi_id).filter(Seat.row == seat_row).filter(Seat.col == seat_col).all()
            # print(seat_qry_result)
            seat_qry_result = seat_qry_result[0]
            seat_reserve.reservation = reserve
            seat_reserve.seats = seat_qry_result
            if seat_col == 5:
                seat_col = 0
                seat_row = chr(ord(seat_row) + 1)
            seat_col += 1
            session.add(seat_reserve)
        # print(reserve.customer)
        # print(reserve.screening)
        # for i in reserve.reserve_seating:
            # print("Here")
            # print(i.seats)
        # print(reserve.reserve_seating)
        screening_qry_result.seat_row_available = seat_row
        screening_qry_result.seat_col_available = seat_col
        screening_qry_result.seats_available -= request_num_seats
        session.add(reserve)
        session.commit()
        session.close()
        return_string_after_reservation = "Reservation successful"
        for i in seats_booked:
            return_string_after_reservation += f" {i[0]}-{i[1]},"
        return return_string_after_reservation[:-1]

def get_reservations():
    
    if not session_customerID:
        return "Login to continue"

    session = get_session()
    customer_qry_result = session.query(Customer).filter(Customer.id == session_customerID).all()
    # print(customer_qry_result)
    customer_qry_result = customer_qry_result[0]
    customer_reservations_list = customer_qry_result.reservations
    if not customer_reservations_list:
        return "No reservations made"
    # print(customer_reservations_list)
    customer_reservations = {}
    for reservation in customer_reservations_list:
        
        customer_reservations[reservation.id] = {"Auditorium":reservation.screening.auditorium.name}
        # print(type(reservation.reserve_seating))
        customer_reservations[reservation.id]["Seating"] = []
        for i in reservation.reserve_seating:
        #     print(i)
        #     type(i)
            customer_reservations[reservation.id]["Seating"].append(f"{i.seats.row}-{i.seats.col}")

    return customer_reservations