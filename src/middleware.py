from datetime import datetime

from icecream import ic
from sqlalchemy import select
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, AuthenticationError
from starlette.config import Config
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import HTTPConnection, Request
from starlette.responses import JSONResponse

from config.database import database
from src.models import players

config = Config('.env')
URL = config('URL')


class AuthMiddleware(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        if "Authorization" not in conn.headers:
            return
        auth_header = conn.headers["Authorization"]
        credentials = conn.headers["Credentials"]
        token = auth_header.split(" ")[1]
        query = select(players.c.token, players.c.username, players.c.expiry_date).where(
            players.c.id == int(credentials))
        data = await database.fetch_one(query)
        if data is None or token != data['token'] or (data['expiry_date'] < datetime.now()):
            raise AuthenticationError('invalid token')
        return AuthCredentials(["authenticated"]), SimpleUser(data['username'])


def auth_error(request: Request, exc: Exception):
    return JSONResponse(status_code=401, content={'error': str(exc)})


middleware = [
    Middleware(AuthenticationMiddleware, backend=AuthMiddleware(), on_error=auth_error),
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts=[URL],
    ),
    # Middleware(HTTPSRedirectMiddleware)

]
