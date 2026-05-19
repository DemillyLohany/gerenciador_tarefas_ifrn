from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from jose import jwt

from database import create_db, get_session
from model import Usuarios, UsuarioLogin, UsuarioCria

from passlib.context import CryptContext

#define o algoritmo de hash pra senha_hash (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(password: str):
    return pwd_context.hash(password)

SessionDep = Annotated[Session, Depends(get_session)]

# chave secreta do projeto pra o token
SECRET_KEY = "sua_chave_secreta_super_protegida_camila_demilly_filipe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# função pra criar o token de acesso que vai ser utilizado
def criar_token_acesso(dados: dict):
    para_codificar = dados.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    para_codificar.update({"exp": expiracao})
    return jwt.encode(para_codificar, SECRET_KEY, algorithm=ALGORITHM)

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
def cadastrar_usuario(usuario: UsuarioCria,session:SessionDep):#recebe os dados enviados que estão na classe de usuários (com o session, se conecta com o banco)
    novo_usuario = Usuarios(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha) # Transforma a senha em texto claro em um hash seguro
    )

    session.add(novo_usuario) # Diz que quer salvar o usuário, m s só salva de verdade...
    session.commit()#aqui
    session.refresh(novo_usuario) #atualiza as coisa com os dados do banco

    return novo_usuario #Agora o usuário cadastrado é retornado (com o ID gerado pelo banco)

@app.post('/login')
def login(dados: UsuarioLogin, session: SessionDep):
    usuario = session.exec(select(Usuarios).where(Usuarios.email == dados.email)).first()
    if not usuario:
      raise HTTPException(401,"E-mail ou senha incorretos")
    
    #verifica se a senha enviada bate com a senha_hash cadastrada no banco
    if not pwd_context.verify(dados.senha, usuario.senha_hash):
        raise HTTPException(401, "E-mail ou senha incorretos")
    
    #cria o Token JWT para manter a aplicação stateless (sem estado)
    token = criar_token_acesso(dados={"sub": usuario.email})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {"nome": usuario.nome, "email": usuario.email}
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

# - Backend seguinte: Tarefas
# - Backend seguinte: Tarefas
# - Proteção de Rotas(usando Depends): pras rotas de tarefas (tipo editar) só funcionem 
# se o usuário enviar esse access_token aí no cabeçalho da requisição. 
# - Implementar NextJS como ferramenta do Frontend das rotas acima.
# - Trocar o Login por JWT: a autenticação por JWT (JSON Web Token)

