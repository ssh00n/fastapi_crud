from fastapi import FastAPI
from routers import users, boards, posts
from models import init_db
from database import engine


app = FastAPI()

app.include_router(users.router)
app.include_router(boards.router)
app.include_router(posts.router)


@app.on_event("startup")
async def startup_event():
    await init_db(engine)


@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()


@app.get("/")
def read_root():
    return {"Hello": "World"}
