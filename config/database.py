import os

from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.config import Config

config = Config('.env')
DATABASE_URL = config('DATABASE_URL')

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()


def create_db():
    if not os.path.exists(DATABASE_URL):
        metadata.create_all(engine)
