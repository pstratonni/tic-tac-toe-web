from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, text

from config.database import metadata

players = Table(
    'players',
    metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True, nullable=False),
    Column('username', String, unique=True),
    Column('games_won', Integer, index=True, server_default=text('0'), nullable=False),
    Column('draw', Integer, index=True, server_default=text('0'), nullable=False),
    Column('total_games', Integer, server_default=text('0'), nullable=False),
    Column('password', String, nullable=False),
    Column('token', String, nullable=True),
    Column('expiry_date', DateTime, nullable=True),
    Column('is_superuser', Boolean, server_default=text('FALSE'))
)

