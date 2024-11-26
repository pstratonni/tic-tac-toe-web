from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

template = Jinja2Templates(directory='templates')


class HomePage(HTTPEndpoint):
    async def get(self, request):
        return template.TemplateResponse('index.html', {'request': request})


class SignIn(HTTPEndpoint):
    encoding = 'json'
    async def get(self, request):
        return template.TemplateResponse('sign_in.html', {'request': request})

    async def post(self, request):

        body = await request.json()
        print(body)
        return JSONResponse(status_code=200, content={'name':'name'})
