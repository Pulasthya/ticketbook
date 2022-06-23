from sql_utils.utils import *
from tables.tables import *

def get_available_seats_screening(screening_id):
    session = get_session()
    # print(session.query(Screening).all())

    reservations_qry_result = session.query(Reservation).filter(Reservation.screening_id == screening_id).all()
    # print(reservations_qry_result)
    reserved_seats_objects = []
    for i in reservations_qry_result:
        reserved_seats_objects += i.reserve_seating
        # print(i.reserve_seating)

    reserved_seats = set()
    # print(reserved_seats_objects)
    for i in reserved_seats_objects:
        # print(i.seats.row, i.seats.col)
        # print(type(i.seats))
        reserved_seats.add(f"{i.seats.row}-{i.seats.col}")
    print(reserved_seats)
    session.close()
    all_seats = {'A-2', 'D-3', 'D-5', 'C-1', 'C-5', 'A-1', 'A-5', 'D-1', 'C-3', 'C-2', 'D-4', 'D-2', 'B-3', 'A-3', 'B-4', 'B-5', 'A-4', 'B-2', 'B-1', 'C-4'}

    # print(all_seats - reserved_seats)
    return all_seats - reserved_seats