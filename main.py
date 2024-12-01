from starlette.applications import Starlette

from config.database import database, create_db
from src.middleware import middleware

from src.routes import routes

app = Starlette(debug=True, routes=routes,
                middleware=middleware
                )


@app.on_event('startup')
async def on_startup():
    await database.connect()
    create_db()


@app.on_event('shutdown')
async def on_shutdown():
    await database.disconnect()


