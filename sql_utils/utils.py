import uuid

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')

Base = declarative_base()

Session = sessionmaker(bind=engine)

def get_session():
    session = Session()
    return session

def generate_uuid():
    return str(uuid.uuid4())