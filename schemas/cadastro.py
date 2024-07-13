from pydantic import BaseModel, EmailStr

# Schema para o cadastro
class CadastroSchema(BaseModel):
    Email: str
    Senha: str
    CEP: str
    
 # Schema para o login  
class LoginSchema(BaseModel):
    Email: str
    Senha: str
    
# Schema para as compras (Deve ser passado o ID na rota)
class CompraIdForm(BaseModel):
    compra_id: int
    

# Schema para atualizar cep
class AtualizarCEPSchema(BaseModel):
    CEP: str
    

