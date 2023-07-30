from fastapi import FastAPI
from routers import users, boards

app = FastAPI()

app.include_router(users.router)
app.include_router(boards.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
