import asyncio

from fastapi import FastAPI

app = FastAPI()


# Serviços simulados
async def buscar_estoque(cliente_id):
    await asyncio.sleep(0.3)

    return {"cliente_id": cliente_id, "produtos_em_estoque": 10}


async def buscar_financeiro(cliente_id, falhar=False):
    await asyncio.sleep(0.7)

    if falhar:
        raise ConnectionError("Serviço financeiro indisponível")

    return {"cliente_id": cliente_id,"credito": 1000}


async def buscar_cliente(cliente_id):
    await asyncio.sleep(0.5)

    return {"id": cliente_id,"nome": "Cainã"}


# Consulta um serviço com timeout e duas tentativas
async def consultar_servico(nome, service):
    for tentativa in range(2):
        try:
            return await asyncio.wait_for(service(),timeout=1,)

        except Exception as erro:
            if tentativa == 0:
                await asyncio.sleep(0.1)
            else:
                return {"erro": f"Não foi possível consultar {nome}: {erro}"}


@app.get("/consulta/{cliente_id}")
async def consultar_dados_cliente(cliente_id,falhar_financeiro=False):
    estoque, financeiro, cliente = await asyncio.gather(
        consultar_servico("estoque",lambda: buscar_estoque(cliente_id),),
        consultar_servico("financeiro",lambda: buscar_financeiro(cliente_id, falhar_financeiro),),
        consultar_servico("cliente",lambda: buscar_cliente(cliente_id),),)

    return {"cliente_id": cliente_id,"estoque": estoque,"financeiro": financeiro,"cliente": cliente,}






