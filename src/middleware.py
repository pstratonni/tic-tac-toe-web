from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

config = Config('.env')
URL = config('URL')
middleware = [
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts=['*'],
    ),
    Middleware(HTTPSRedirectMiddleware)
]
