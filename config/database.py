import os

from databases import Database
from sqlalchemy import create_engine, MetaData


DATABASE_URL = 'sqlite:///my.db'
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
metadata = MetaData()


def create_db():
    if not os.path.exists(DATABASE_URL):
        metadata.create_all(engine)
