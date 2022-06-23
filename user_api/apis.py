import json
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from sql_utils.utils import get_session
from tables.tables import *
from user_api.helper import *

session_customerID = None

def sign_up():

    if session_customerID:
        return jsonify({"message": "Currently logged in. Please try after logging out"}), 400
    content_type = request.headers.get('Content-Type')
    if (content_type == "application/json"):
        data = request.get_json()
        if "name" not in data or "password" not in data or "phone_number" not in data or "age" not in data or not isinstance(data["name"], str) or not isinstance(data["password"], str) or not isinstance(data["phone_number"], str) or not isinstance(data["age"], int) or len(data["phone_number"]) != 10:
            return jsonify({"message": "Incorrect or no data provided"}), 400
        session = get_session()
        if session.query(Customer).filter(Customer.phone_number == data["phone_number"]).all():
            session.close()
            return jsonify({"message": "Customer already exists"}), 400
        new_customer = Customer(data["name"], data["phone_number"], data["age"], generate_password_hash(data["password"], method='sha256'))
        session.add(new_customer)
        session.commit()
        session.close()
        return jsonify({"message": f"Account for user {data['name']} has been created successful"})
    return jsonify({"message": "Mis-Match in Content-Type"}), 400

def login():

    global session_customerID
    if session_customerID != None:
        return jsonify({"message": "Currently logged in. Logout and try again"}), 400
    content_type = request.headers.get('Content-Type')
    if (content_type == "application/json"):
        data = request.get_json()
        if "phone_number" not in data or "password" not in data or not isinstance(data["phone_number"], str) or not isinstance(data["password"], str) or len(data["phone_number"]) != 10:
            return jsonify({"message": "Incorrect or no data provided"}), 400
        session = get_session()
        customer_qry_result = session.query(Customer).filter(Customer.phone_number == data["phone_number"])
        if not customer_qry_result:
            session.close()
            return jsonify({"message": f"User {data['phone_number']} does not exist"}), 400
        user = customer_qry_result[0]
        if not (check_password_hash(user.password, data["password"])):
            session.close()
            return jsonify({"message": "Invalid credentials passed"}), 400
        
        session_customerID = user.id
        session.close()
        return jsonify({"message": f"Successfully logged in {user.name}"})
    return jsonify({"message": "Mis-Match in Content-Type"}), 400

def logout():
    global session_customerID
    if not session_customerID:
        return jsonify({"message": "No account is logged in"}), 400
    session_customerID = None
    return jsonify({"message": "Successfully logged out"})

def get_movies():
    if not session_customerID:
        return jsonify({"message":"Login to continue"}), 400
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
        return jsonify({"message":"Login to continue"}), 400
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        data = request.get_json()
        print(type(data["movie_id"]))
        if "movie_id" not in data or not data or not isinstance(data["movie_id"], str) or not data["movie_id"]:
            return jsonify({"message":"Incorrect or no data provided"}), 400
        movie_id = data["movie_id"]
        session = get_session()
        qry_result = session.query(Screening).filter(Screening.movie_id == movie_id).all()
        # print(qry_result)
        if not qry_result:
            session.close()
            return jsonify({"Message":"Sorry, currently no screenings"}), 400
        screenings = {}
        for result in qry_result:
            # print(type(result.id), type(result.auditorium.name), type(result.movie.movie_name), type(result.date), type(result.start_time))
            screenings[result.id] = {"Auditorium":result.auditorium.name, "Movie Name":result.movie.movie_name, "Date":str(result.date), "Start-Time": str(result.start_time), "Available Seats": list(get_available_seats_screening(result.id))}
        # print(type(screenings), screenings)
        session.close()
        return json.dumps(screenings)
    return jsonify({"message":"Mis-Match in Content-Type"}), 400

def make_reservation():
    print(session_customerID)

    if not session_customerID:
        return jsonify({"message": "Login to continue"}), 400
    
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        data = request.get_json()
        # print(data["screening_id"], data["seats"])
        # print(type(data["screening_id"]), type(data["seats"]))
        if not data or "screening_id" not in data or "seats" not in data or not isinstance(data["screening_id"], str) or not isinstance(data["seats"], list):
            return jsonify({"Message":"Incorrect or no data provided"}), 400
        for seat in data["seats"]:
            seat_split = seat.split("-")
            if not isinstance(seat, str) or not seat_split[0].isalpha() or not seat_split[1].isnumeric():
                return jsonify({"Message":"Incorrect or no data provided"}), 400
        
        session = get_session()
        screening_qry_result = session.query(Screening).filter(Screening.id == data["screening_id"]).all()
        if not screening_qry_result:
            session.close()
            return jsonify({"Message": "Enter a valid screening id"}), 400
        screening_qry_result = screening_qry_result[0]

        if screening_qry_result.seats_available == 0:
            session.close()
            return jsonify({"Message": "All seats are booked"}), 400
        
        request_num_seats = len(data["seats"])
        if request_num_seats < 1 or request_num_seats < len(data["seats"]):
            session.close()
            return jsonify({"Message": "Please request for a valid number of seats"}), 400

        available_seats_request_screening = get_available_seats_screening(data["screening_id"])
        for seat in data["seats"]:
            if seat not in available_seats_request_screening:
                session.close()
                return jsonify({"message": "Make sure to enter valid seats"}), 400
        
        reserve = Reservation(request_num_seats)
        loggedin_customer = session.query(Customer).filter(Customer.id == session_customerID).all()[0]
        reserve.customer = loggedin_customer
        reserve.screening = screening_qry_result

        for seat in data["seats"]:
            seat_split = seat.split("-")
            seat_row = seat_split[0]
            seat_col = seat_split[1]
            seat_reserve = Reservation_Seating()
            seat_qry_result = session.query(Seat).filter(Seat.audi_id == screening_qry_result.audi_id).filter(Seat.row == seat_row).filter(Seat.col == seat_col).all()
            # print(seat_qry_result)
            seat_qry_result = seat_qry_result[0]
            seat_reserve.reservation = reserve
            seat_reserve.seats = seat_qry_result
            session.add(seat_reserve)

        # print(reserve.customer)
        # print(reserve.screening)
        # for i in reserve.reserve_seating:
        #     print("Here")
        #     print(i.seats)
        # print(reserve.reserve_seating)
        screening_qry_result.seat_row_available = seat_row
        screening_qry_result.seat_col_available = seat_col
        screening_qry_result.seats_available -= request_num_seats
        session.add(reserve)
        session.commit()
        session.close()

        return jsonify({"Message": "Reservation successful"})


    return jsonify({"Message": "Mis-Match in Content-Type"}), 400

def make_reservation_old():

    if not session_customerID:
        return jsonify({"message": "Login to continue"}), 400
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        data = request.get_json()
        print(type(data["screening_id"]))
        if "screening_id" not in data or "num_seats" not in data or not data or not isinstance(data["screening_id"], str) or not isinstance(data["num_seats"], int):
            return jsonify({"Message":"Incorrect or no data provided"}), 400
        
        request_screening_id = data["screening_id"]
        request_num_seats = data["num_seats"]
        
        session = get_session()
        screening_qry_result = session.query(Screening).filter(Screening.id == request_screening_id).all()
        if not screening_qry_result:
            return jsonify({"Message": "Enter a valid screening id"}), 400
        screening_qry_result = screening_qry_result[0]
        # print(type(screening_qry_result))
        # print(screening_qry_result)
        if screening_qry_result.seats_available == 0:
            return jsonify({"Message": "All seats are booked"}), 400
        # print(screening_qry_result.seats_available, request_num_seats)
        if request_num_seats < 1 or screening_qry_result.seats_available < request_num_seats:
            # print("hererererere")
            return jsonify({"Message": "Please request for a valid number of seats"}), 400
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
    return jsonify({"Message": "Mis-Match in Content-Type"}), 400

def get_reservations():
    
    if not session_customerID:
        return jsonify({"Message": "Login to continue"}), 400

    session = get_session()
    customer_qry_result = session.query(Customer).filter(Customer.id == session_customerID).all()
    # print(customer_qry_result)
    customer_qry_result = customer_qry_result[0]
    customer_reservations_list = customer_qry_result.reservations
    if not customer_reservations_list:
        return jsonify({"Message": "No reservations made"}), 400
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