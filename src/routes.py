from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from src.endpoints import HomePage, SignIn, Create, AvailableName
from src.ws import WSGame

routes = [
    Route('/', HomePage),
    Route('/sign_in', SignIn),
    Route('/create', Create),
    Route('/available', AvailableName),
    WebSocketRoute('/ws', WSGame),
    Mount('/static/', app=StaticFiles(directory='static'))
]
