from common.routes import configure_app
from sql_utils.utils import *

from tables.tables import *
from flask import Flask, jsonify

Base.metadata.create_all(engine)

# from tables.data_entry import *

app = Flask(__name__)

configure_app(app)

# if __name__ == "__main__":
    
    # session = get_session()
    # print(session.query(Movie).all())
    # app.run(debug=True)
    # pass