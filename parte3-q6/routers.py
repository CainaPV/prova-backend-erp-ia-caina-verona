import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import usuario_atual
from cache import invalidar_listas_de_produtos, ler_cache, salvar_cache
from database import get_db
from fila import alertar_estoque_baixo
from models import Produto
from schemas import PaginaProdutos, ProdutoCreate, ProdutoResponse, ProdutoUpdate


router = APIRouter(prefix="/produtos", dependencies=[Depends(usuario_atual)])


async def produto_por_id(id: int, db: AsyncSession) -> Produto:
    produto = await db.get(Produto, id)
    if not produto:
        raise HTTPException(404, "Produto não encontrado")
    return produto


async def atualizar_cache_e_fila(produto: Produto) -> None:
    await invalidar_listas_de_produtos()
    alertar_estoque_baixo(produto)


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar(dados: ProdutoCreate, db: AsyncSession = Depends(get_db)):
    produto = Produto(**dados.model_dump())
    db.add(produto)
    await db.commit()
    await db.refresh(produto)
    await atualizar_cache_e_fila(produto)
    return produto


@router.get("", response_model=PaginaProdutos)
async def listar(
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(10, ge=1, le=100),
    nome: str | None = None,
    preco_min: Decimal | None = Query(None, ge=0),
    preco_max: Decimal | None = Query(None, ge=0),
    estoque_baixo: bool = False,
    db: AsyncSession = Depends(get_db),
):
    if preco_min is not None and preco_max is not None and preco_min > preco_max:
        raise HTTPException(422, "preco_min não pode ser maior que preco_max")

    chave = f"produtos:list:{pagina}:{tamanho}:{nome}:{preco_min}:{preco_max}:{estoque_baixo}"
    if resposta_cache := await ler_cache(chave):
        return json.loads(resposta_cache)

    filtros = []
    if nome:
        filtros.append(Produto.nome.ilike(f"%{nome}%"))
    if preco_min is not None:
        filtros.append(Produto.preco >= preco_min)
    if preco_max is not None:
        filtros.append(Produto.preco <= preco_max)
    if estoque_baixo:
        filtros.append(Produto.quantidade_em_estoque <= 10)

    total = await db.scalar(select(func.count()).select_from(Produto).where(*filtros)) or 0
    produtos = await db.scalars(
        select(Produto).where(*filtros).offset((pagina - 1) * tamanho).limit(tamanho)
    )
    resposta = PaginaProdutos(
        pagina=pagina,
        tamanho=tamanho,
        total=total,
        itens=[ProdutoResponse.model_validate(item) for item in produtos],
    ).model_dump(mode="json")
    await salvar_cache(chave, json.dumps(resposta))
    return resposta


@router.get("/{id}", response_model=ProdutoResponse)
async def obter(id: int, db: AsyncSession = Depends(get_db)):
    return await produto_por_id(id, db)


@router.put("/{id}", response_model=ProdutoResponse)
async def atualizar(id: int, dados: ProdutoUpdate, db: AsyncSession = Depends(get_db)):
    produto = await produto_por_id(id, db)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    await db.commit()
    await db.refresh(produto)
    await atualizar_cache_e_fila(produto)
    return produto


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir(id: int, db: AsyncSession = Depends(get_db)):
    await db.delete(await produto_por_id(id, db))
    await db.commit()
    await invalidar_listas_de_produtos()
    return Response(status_code=204)
