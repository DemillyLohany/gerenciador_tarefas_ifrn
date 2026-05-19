from sqlmodel import SQLModel, Field, create_engine, Relationship
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, List

class UsuarioCria(SQLModel):
    nome: str
    email: str
    senha: str

class UsuarioLogin(SQLModel):
    email: str
    senha: str

class Usuarios(SQLModel, table=True):
    __tablename__: str = 'usuarios'
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(sa_column_kwargs={"unique": True})
    senha_hash: str = Field(max_length=72) 

    tarefas: List["Tarefas"] = Relationship(back_populates="usuario")

class Tarefas(SQLModel, table=True):
    __tablename__: str = 'tarefas'
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key='usuarios.id')
    titulo: str
    status: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    data_entrega: Optional[date] = None
    data_entrega_real: Optional[datetime] = None

    usuario: Optional["Usuarios"] = Relationship(back_populates="tarefas")

