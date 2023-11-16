from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from src.endpoints import HomePage
from src.ws import WSGame

routes = [
    Route('/', HomePage),
    WebSocketRoute('/ws', WSGame),
    Mount('/static/', app=StaticFiles(directory='static'))
]
