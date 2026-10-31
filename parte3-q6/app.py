from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import models
from auth import criar_token, login_valido
from database import Base, engine
from routers import router
from schemas import Login, Token


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)
    yield


app = FastAPI()
app.include_router(router)


@app.post("/auth/login", response_model=Token)
async def login(dados: Login):
    if not login_valido(dados.usuario, dados.senha):
        raise HTTPException(401, "Credenciais inválidas")
    return {"access_token": criar_token(dados.usuario)}


@app.get("/")
async def inicio():
    return {"status": "ok"}
