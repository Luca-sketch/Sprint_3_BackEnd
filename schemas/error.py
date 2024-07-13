from pydantic import BaseModel

# Schema para lidar com os erros
class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro será representada """
    message: str