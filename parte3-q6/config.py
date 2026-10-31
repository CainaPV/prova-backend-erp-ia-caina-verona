import os

from dotenv import load_dotenv


load_dotenv()


def env(nome):
    valor = os.getenv(nome)
    if not valor:
        raise RuntimeError(f"Variável de ambiente obrigatória: {nome}")
    return valor
