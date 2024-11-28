from icecream import ic
from sqlalchemy import select
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse

from config.database import database
from src.models import players

config = Config('.env')
URL = config('URL')


class AuthMiddleware(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return
        auth_header = conn.headers["Authorization"]
        credentials = conn.headers["Credentials"]
        token = auth_header.split(" ")[1]
        query = select(players.c.token, players.c.username, players.c.expiry_date).where(players.c.id == int(credentials))
        data = await database.fetch_one(query)
        ic(data['expiry_date'])
        if data is None or token != data['token']:
            return JSONResponse({}, status_code=401)
        return AuthCredentials(["authenticated"]), SimpleUser(data['username'])


middleware = [
    Middleware(AuthenticationMiddleware, backend=AuthMiddleware())
    # Middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=['*'],
    # ),
    # Middleware(HTTPSRedirectMiddleware)

]
