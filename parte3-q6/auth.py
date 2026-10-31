from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import env

CHAVE = env("JWT_SECRET")
bearer = HTTPBearer()


def login_valido(usuario, senha):
    return usuario == env("ADMIN_USER") and senha == env("ADMIN_PASSWORD")


def criar_token(usuario):
    dados = {"sub": usuario, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(dados, CHAVE, algorithm="HS256")


async def usuario_atual(credenciais: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(credenciais.credentials, CHAVE, algorithms=["HS256"])["sub"]
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(401, "Token inválido ou expirado")
