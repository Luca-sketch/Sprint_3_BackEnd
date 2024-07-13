from pydantic import BaseModel

# Schema para adicionar um novo item ao carrinho
class CarrinhoSchema(BaseModel):  
    Produto: str
    Valor: str
    Onda: str
  

