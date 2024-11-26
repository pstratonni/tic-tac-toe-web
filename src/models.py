from sqlalchemy import Table, Column, Integer, String

from config.database import metadata



players = Table(
    'players',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String),
    Column('games_won', Integer, index=True),
    Column('total_games', Integer),
    Column('password', String)
)
