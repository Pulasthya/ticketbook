import user_api

api_routes = user_api.api_routes

def configure_app(app):
    for route in api_routes:
        api_url = route[0]
        handler = route[1]
        methods = route[2]
        app.add_url_rule(api_url, f"{route}|{handler}", handler, methods=methods)