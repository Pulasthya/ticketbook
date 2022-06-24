from sqlalchemy.orm import relationship

from sqlalchemy import Column, ForeignKey, String, Integer, Date, DateTime, Boolean, CHAR, Time

from sql_utils.utils import *

class Movie(Base):

    __tablename__ = "movie"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    movie_name = Column(String, nullable=False, unique=True)
    release_date = Column(Date, nullable=False)
    duration = Column(Integer, nullable=False)
    director = Column(String, nullable=False)

    screenings = relationship("Screening", back_populates="movie")

    def __init__(self, movie_name, release_date, duration, director):
        self.movie_name = movie_name
        self.release_date = release_date
        self.duration = duration
        self.director = director

    def __repr__(self) -> str:
        return f"Movie Name : {self.movie_name}, Movie ID : {self.id}, Release Date : {self.release_date}, Duration : {self.duration}, Director : {self.director}"

class Customer(Base):

    __tablename__ = "customer"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    reservations = relationship("Reservation", back_populates="customer")

    def __init__(self, name, phone_number, age, password):
        self.name = name
        self.phone_number = phone_number
        self.age = age
        self.password = password

    def __repr__(self) -> str:
        return f"Customer Name : {self.name}, Cust ID : {self.id} Customer Phone : {self.phone_number}, Customer Age : {self.age}"


class Auditorium(Base):
    
    __tablename__ = "auditorium"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    num_seats = Column(Integer, nullable=False)

    screeings = relationship("Screening", back_populates="auditorium")
    seats = relationship("Seat", back_populates="auditorium")

    def __init__(self, name, num_seats):
        self.name = name
        self.num_seats = num_seats

    def __repr__(self) -> str:
        return f"Auditorium Name : {self.name}, Audi ID : {self.id}, seats : {self.num_seats}"

class Screening(Base):

    __tablename__ = "screening"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audi_id = Column(String(36), ForeignKey("auditorium.id"))
    movie_id = Column(String(36), ForeignKey("movie.id"))
    start_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)
    end_time = Column(Time, nullable=False)
    seats_available = Column(Integer, default=20)

    auditorium = relationship("Auditorium", back_populates="screeings")
    movie = relationship("Movie", back_populates="screenings")
    reservations = relationship("Reservation", back_populates="screening")
    reservation = relationship("Reservation_Seating", back_populates="screening")

    def __init__(self, start_time, date, end_time):
        self.start_time = start_time
        self.date = date
        self.end_time = end_time

    def __repr__(self) -> str:
        return f"Auditorium : {self.auditorium.name}, Scr ID : {self.id}, Seats Available : {self.seats_available} Movie : {self.movie.movie_name}, Start-Time : {self.start_time}"

class Seat(Base):

    __tablename__ = "seat"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    row = Column(CHAR, nullable=False)
    col = Column(Integer, nullable=False)
    audi_id = Column(String(36), ForeignKey("auditorium.id"))

    auditorium = relationship("Auditorium", back_populates="seats")
    reservation_seatings = relationship("Reservation_Seating", back_populates="seats", uselist=False)

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self) -> str:
        return f"ID: {self.id}, Row : {self.row}, Col : {self.col}, Audi : {self.auditorium.name}"

class Reservation(Base):

    __tablename__ = "reservation"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cust_id = Column(String(36), ForeignKey("customer.id"))
    screening_id = Column(String(36), ForeignKey("screening.id"))
    seats = Column(Integer, nullable=False)

    def __init__(self, seats):
        self.seats = seats

    def __repr__(self) -> str:
        return f"Reservation ID : {self.id} Customer : {self.customer.name}, Screen : {self.screening.auditorium.name}, Seats : {self.reserve_seating}"

    customer = relationship("Customer", back_populates="reservations")
    screening = relationship("Screening", back_populates="reservations")
    reserve_seating = relationship("Reservation_Seating", back_populates="reservation")

class Reservation_Seating(Base):

    __tablename__ = "reservation_seating"

    # id = Column(String(36), primary_key=True, default=generate_uuid)
    reserve_id = Column(String(36), ForeignKey("reservation.id"), primary_key=True)
    seat_id = Column(String(36), ForeignKey("seat.id"), primary_key=True)
    screening_id = Column(String(36), ForeignKey("screening.id"))

    # def __repr__(self) -> str:
    #     return f"{self.seats.row}-{self.seats.col} "

    screening = relationship("Screening", back_populates="reservation")
    reservation = relationship("Reservation", back_populates="reserve_seating")
    seats = relationship("Seat", back_populates="reservation_seatings")