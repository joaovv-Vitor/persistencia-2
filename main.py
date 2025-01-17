from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_db_and_tables
from rotas import album, perfil, pubAlbum, publicacao


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(perfil.router)
app.include_router(publicacao.router)
app.include_router(album.router)
app.include_router(pubAlbum.router)
