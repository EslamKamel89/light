from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header, Path, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from exceptions import APIException, api_exception_handler, validation_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup COMPLETED")
    yield
    print("shutdown: cleaning up")


app = FastAPI(title="Light 💡", lifespan=lifespan)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def home():
    return {"message": "Welcome to Light 💡, Next level book store API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/great/{name}")
async def great(
    name: Annotated[str, Path(min_length=1, max_length=50)],
    age: Annotated[int | None, Query(gt=10, lt=100)] = None,
):
    if age and age < 16:
        raise APIException(
            status_code=400, message="Your are too young, come back few years later"
        )
    return {
        "message": f"Welcome {name}",
        "age": age if age else "You didn't enter your age",
    }


class InfoModel(BaseModel):
    name: str
    age: int
    hobbies: list[str]


@app.post("/info")
async def info(info: InfoModel, secret: Annotated[str, Header()]):
    if secret != "carrot":
        raise APIException(status_code=400, message="You don't know the secret word")
    return info
