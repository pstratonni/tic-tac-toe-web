from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from src.endpoints import HomePage, SignIn
from src.ws import WSGame

routes = [
    Route('/', HomePage, name='Home Page'),
    Route('/sign_in', SignIn),
    WebSocketRoute('/ws', WSGame),
    Mount('/static/', app=StaticFiles(directory='static'))
]
