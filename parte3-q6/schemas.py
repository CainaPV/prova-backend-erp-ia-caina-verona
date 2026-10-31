from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    preco: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    quantidade_em_estoque: int = Field(ge=0)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str):
        valor = valor.strip()
        if not valor or valor.isnumeric():
            raise ValueError("nome não pode ser vazio ou somente números")
        return valor


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=100)
    preco: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    quantidade_em_estoque: int | None = Field(None, ge=0)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str | None):
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor or valor.isnumeric():
            raise ValueError("nome não pode ser vazio ou somente números")
        return valor


class ProdutoResponse(ProdutoCreate):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginaProdutos(BaseModel):
    pagina: int
    tamanho: int
    total: int
    itens: list[ProdutoResponse]


class Login(BaseModel):
    usuario: str
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
