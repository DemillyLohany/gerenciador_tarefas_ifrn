from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlmodel import Session, select
from contextlib import asynccontextmanager

from database import create_db, get_session
from model import Usuarios, UsuarioLogin, UsuarioCria

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield
    
app = FastAPI(lifespan=lifespan)

# rota raiz
@app.get("/")
def home():
    return {"ok": True}

# Rotas do usuário

@app.post('/usuarios') #Criando a rotinha de cadastro
def cadastrar_usuario(usuario:Usuarios,session:SessionDep):#recebe os dados enviados que estão na classe de usuários (com o session, se conecta com o banco)
    session.add(usuario) # Diz que quer salvar o usuário, m s só salva de verdade...
    session.commit()#aqui
    session.refresh(usuario) #atualiza as coisa com os dados do banco

    return usuario #Agora o usuário cadastrado é retornado


@app.post('/login')
def login(dados: UsuarioLogin, session: SessionDep):
    usuario = session.exec(select(Usuarios).where(Usuarios.email == dados.email)).first()
    if usuario is None:
      raise HTTPException(401,"Usuario não encontrado")
    
    if usuario.senha_hash != dados.senha:
        raise HTTPException(401,"Senha incorreta")
    return {
        "mensagem": "Login realizado"
    }

@app.get('/usuarios/{id}')
def perfil_usuario(id: int, session: SessionDep):
    usuario = session.get(Usuarios, id)

    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado")
    
    return usuario

@app.put('/usuarios/{id}')
def atualizar_usuario(id:int, usuario:Usuarios, 
session:SessionDep) -> Usuarios:
    usuarioUpdate = session.get(Usuarios, id)

    if usuarioUpdate is None:
        raise HTTPException(404, "Usuario não encontrado")

    usuarioUpdate.email = usuario.email
    usuarioUpdate.nome = usuario.nome
    usuarioUpdate.senha_hash = usuario.senha_hash

    session.add(usuarioUpdate)
    session.commit()
    session.refresh(usuarioUpdate)

    return usuarioUpdate

@app.delete("/usuarios/{id}")
def deletar_usuario(id: int, session: SessionDep):
    usuario = session.get(Usuarios, id)

    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado")
    
    session.delete(usuario)

    session.commit()

    return {"mensagem": "Conta deletada com sucesso"}

# Próximas etapas:
# - Trocar o Login por JWT: a autenticação por JWT (JSON Web Token)
# - Implementar NextJS como ferramenta do Frontend das rotas acima
# - Backend seguinte: Tarefas





