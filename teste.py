#pip install fastapi
# uvicorn email-valitador
from pydantic import BaseModel
from pydantic import EmailStr

class Usuario(BaseModel):
    nome:str
    cpf:str
    email:EmailStr