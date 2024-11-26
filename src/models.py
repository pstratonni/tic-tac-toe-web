from sqlalchemy import Table, Column, Integer, String

from config.database import metadata

players = Table(
    'players',
    metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True, nullable=False),
    Column('username', String, unique=True),
    Column('games_won', Integer, index=True, insert_default=0, nullable=False),
    Column('draw', Integer, index=True, insert_default=0, nullable=False),
    Column('total_games', Integer, insert_default=0, nullable=False),
    Column('password', String, nullable=False),
    Column('token', String, nullable=True)
)
su = Table(
    'su',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('username', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    Column('token', String, nullable=True)
)
