from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String, func

from database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, index=True)
    preco = Column(Numeric(10, 2), nullable=False)
    quantidade_em_estoque = Column(Integer, nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("preco >= 0"),CheckConstraint("quantidade_em_estoque >= 0"))
