import sqlalchemy
from settings import DATABASE_CONNECTION
from models import Base

engine = sqlalchemy.create_engine(DATABASE_CONNECTION)
Base.metadata.create_all(engine)
