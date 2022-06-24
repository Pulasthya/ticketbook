from tables.tables import *
from datetime import date, time
from werkzeug.security import generate_password_hash, check_password_hash

session = get_session()

vikram = Movie("Vikram", date(2022, 6, 12), 180, "DD")
sundar = Movie("Sundar", date(2022, 7, 1), 180, "Dedeep")
vikram1 = Movie("Vikram1", date(2022, 6, 15), 180, "Pullu")

session.add(vikram)
session.add(sundar)
session.add(vikram1)

# print("Here")

data = (session.query(Movie).all())

for i in data:
    print(i)

kushal = Customer("Kushal", "1234567890", 22, generate_password_hash("Kushal"))
abhi = Customer("Abhishek", "9902930077", 21, generate_password_hash("Abhishek"))

session.add(kushal)
session.add(abhi)

data = session.query(Customer).all()

for i in data:
    print(i)

audi1 = Auditorium("Hall1", 20)
audi2 = Auditorium("Hall2", 20)

session.add(audi1)
session.add(audi2)

data = session.query(Auditorium).all()
for i in data:
    print(i)

for i in data:
    for j in range(4):
        for k in range(1, 6):
            seat = Seat(chr(65 + j), k)
            seat.auditorium = i
            session.add(seat)

for i in data:
    print(i)
    print(i.seats)

scr1 = Screening(time(19, 30), date(2022, 7, 1), time(22, 30))
scr1.auditorium = audi1
scr1.movie = vikram

scr2 = Screening(time(12, 30), date(2022, 7, 2), time(15, 30))
scr2.auditorium = audi2
scr2.movie = sundar

scr3 = Screening(time(13, 30), date(2022, 7, 1), time(16, 30))
scr3.auditorium = audi1
scr3.movie = vikram

scr4 = Screening(time(9, 30), date(2022, 7, 2), time(12, 30))
scr4.auditorium = audi2
scr4.movie = sundar

session.add(scr1)
session.add(scr2)

data = session.query(Screening).all()
for i in data:
    print(i)

# data = session.query(Customer).all()
# print(len(data))
# for i in data:
#     print(i.reservations)

session.commit()
session.close()