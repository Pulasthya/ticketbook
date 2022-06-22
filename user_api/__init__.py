from user_api.apis import *

api_routes = [
    ("/api/get/movies", get_movies, ["GET"]),
    ("/api/get/screenings", get_screening, ["POST"]),
    ("/api/make/reservation", make_reservation, ["POST"]),
    ("/api/get/reservation", get_reservations, ["GET"]),
    ("/api/signup", sign_up, ["POST"]),
    ("/api/login", login, ["POST"]),
    ("/api/logout", logout, ["GET"])
]