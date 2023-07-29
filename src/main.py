from fastapi import FastAPI
import routers.users

app = FastAPI()

app.include_router(routers.users.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
