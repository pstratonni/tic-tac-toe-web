from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from config.database import database, create_db
from src.routes import routes
from starlette.config import Config

config = Config('.env')
URL = config('URL')
middleware = [
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts=['*'],
    ),
    Middleware(HTTPSRedirectMiddleware)
]

app = Starlette(debug=True, routes=routes)


@app.on_event('startup')
async def on_startup():
    await database.connect()
    create_db()


@app.on_event('shutdown')
async def on_shutdown():
    await database.disconnect()
