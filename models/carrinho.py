# Modelo da tabela carrinho

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Carrinho(Base):
    __tablename__ = "Carrinho"
    id = Column(Integer, primary_key=True, autoincrement=True)
    Produto = Column(String(100))
    Valor = Column(String(100))
    Onda = Column(String(100))
    Token = Column(String(200))

