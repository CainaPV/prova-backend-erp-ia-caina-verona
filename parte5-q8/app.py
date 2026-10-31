import re
import sys
from pathlib import Path
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Produto

# Usa a mesma conexão e o mesmo modelo Produto da Parte 3.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "parte3-q6"))

app = FastAPI()


class Pergunta(BaseModel):
    pergunta: str


def interpretar(pergunta: str) -> dict:
    """Converte a pergunta em uma ação simples."""
    texto = pergunta.lower()
    numero = re.search(r"\d+", texto)

    if "estoque" in texto and ("abaixo" in texto or "menor" in texto) and numero:
        return {"tipo": "estoque_abaixo_de", "limite": int(numero.group())}
    if "listar" in texto or "todos os produtos" in texto:
        return {"tipo": "listar_produtos"}
    return {"tipo": "nao_entendida"}


def produto_json(produto: Produto) -> dict:
    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco": float(produto.preco),
        "quantidade_em_estoque": produto.quantidade_em_estoque,
    }


@app.post("/perguntas")
async def responder(dados: Pergunta, db: AsyncSession = Depends(get_db)):
    acao = interpretar(dados.pergunta)

    if acao["tipo"] == "nao_entendida":
        return {"acao_interpretada": acao, "resultados": []}

    consulta = select(Produto).order_by(Produto.id)
    if acao["tipo"] == "estoque_abaixo_de":
        consulta = consulta.where(Produto.quantidade_em_estoque < acao["limite"])

    produtos = await db.scalars(consulta)
    resultados = [produto_json(produto) for produto in produtos]
    return {
        "pergunta": dados.pergunta,
        "acao_interpretada": acao,
        "quantidade_encontrada": len(resultados),
        "resultados": resultados,
    }
