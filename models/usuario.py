# Modelo da tabela usuário

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "Usuario"
    id = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(100))
    Senha = Column(String(255))
    CEP = Column(String(20))
