import asyncio
import getpass

from sqlalchemy import insert, select
from starlette_auth_toolkit.cryptography import PBKDF2Hasher

from config.database import database
from src.models import players


async def create_superuser():
    await database.connect()
    username = input("Enter username:  ")
    while True:
        password = getpass.getpass("Enter password:  ")
        pass_conf = getpass.getpass('Confirm your password:  ')
        if password == pass_conf:
            break
        print("Passwords don't match\ntry again")
    query = select(players.c.id).where(players.c.username == username)
    user = await database.execute(query)
    if user is not None:
        print(f"User with name {username} exist")
        await database.disconnect()
        return
    query = insert(players).values(username=username, password=PBKDF2Hasher().make_sync(password), is_superuser=True)
    await database.execute(query)
    print(f'Superuser {username} created')
    await database.disconnect()

asyncio.run(create_superuser())
