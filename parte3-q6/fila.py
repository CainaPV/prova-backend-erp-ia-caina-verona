from redis import Redis
from rq import Queue

from config import env

def redis_sync():
    return Redis.from_url(env("REDIS_URL"))


def alertar_estoque_baixo(produto):
    if produto.quantidade_em_estoque > 10:
        return
    try:
        Queue("estoque", connection=redis_sync()).enqueue(
            "tarefas.enviar_alerta", produto.id, produto.nome, produto.quantidade_em_estoque
        )
    except Exception:
        pass  # Redis indisponível não impede salvar o produto.
