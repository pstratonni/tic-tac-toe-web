import random
import string
from datetime import datetime, timedelta
from typing import Any

from icecream import ic
from sqlalchemy import select, insert, update
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette_auth_toolkit.cryptography import PBKDF2Hasher

from config.database import database
from src.models import players

template = Jinja2Templates(directory='templates')


class HomePage(HTTPEndpoint):
    async def get(self, request):
        return template.TemplateResponse('index.html', {'request': request})


class SignIn(HTTPEndpoint):
    async def get(self, request):
        return template.TemplateResponse('sign_in.html', {'request': request})

    async def post(self, request):
        hasher = PBKDF2Hasher()
        user = await request.json()
        query = select(players.c.password, players.c.id).where(players.c.username == user['username'])
        pass_db = await database.fetch_one(query)
        if await hasher.verify(user['password'], pass_db['password']):
            all_symbols = string.ascii_letters + string.digits
            token = ''.join(random.choice(all_symbols) for _ in range(20))
            expiry_date = datetime.now() + timedelta(hours=72)
            query_token = update(players).where(players.c.username == user['username']).values(token=token,
                                                                                               expiry_date=expiry_date)
            await database.execute(query_token)
            query = select(players.c.id, players.c.username, players.c.games_won, players.c.draw, players.c.total_games,
                           players.c.token).where(players.c.id == pass_db['id'])
            data = await database.fetch_one(query)
            result = {'flag': True}
            for i in list(data.keys()):
                result[i] = data[i]
            return JSONResponse(status_code=200, content=result)
        else:
            return JSONResponse(status_code=404, content={'flag': False})


class Create(HTTPEndpoint):
    async def get(self, request):
        return template.TemplateResponse('sign_up.html', {'request': request})

    async def post(self, request):
        hasher = PBKDF2Hasher()
        user = await request.json()
        username, password = user['username'], user['password']
        all_symbols = string.ascii_letters + string.digits
        token = ''.join(random.choice(all_symbols) for _ in range(20))
        expiry_date = datetime.now() + timedelta(hours=72)
        query = insert(players).values(username=username, password=hasher.make_sync(password), token=token,
                                       expiry_date=expiry_date)
        await database.execute(query)
        query_get = select(players.c.id, players.c.username, players.c.token).where(players.c.username == username)
        data = await database.fetch_one(query_get)
        result = {}
        for i in list(data.keys()):
            result[i] = data[i]
        return JSONResponse(status_code=201, content=result)


class AvailableName(HTTPEndpoint):
    async def post(self, request):
        username = await request.json()
        query = select(players.c.username).where(players.c.username == username['username'])
        result = await database.fetch_one(query)
        if result:
            return JSONResponse(status_code=200, content={'flag': True})
        else:
            return JSONResponse(status_code=404, content={'flag': False})


class LogOut(HTTPEndpoint):
    async def post(self, request):
        # try:
        pk = await request.json()
        query = update(players).where(players.c.id == int(pk['id'])).values(token=None, expiry_date=None)
        await database.execute(query)
        return JSONResponse(status_code=200, content={})
    # except:
    #     return JSONResponse(status_code=404, content={})
