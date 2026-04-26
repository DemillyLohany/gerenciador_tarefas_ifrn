#python -m pip install python-multipart
#python -m uvicorn app:app --reload
from fastapi import FastAPI, Form #o form s3erve para receber dados enviados em um formulario
from fastapi.responses import HTMLResponse #retorna o HTML
from fastapi.templating import Jinja2Templates # cria templates HTML
from fastapi import Request #permite o acesso e detalhes do HTTP
import sqlite3 #pra o banco de dados

app = FastAPI() # cria o app
templates = Jinja2Templates(directory='templates') #define que os arquivos .html estão em uma página chamada 'templates'

#cria o banco de dados e a tabelinha de usuários
def criar_banco():
    conn = sqlite3.connect('usuario.db') #cria o usuarios.db
    cursor = conn.cursor() #o SQL é executado por meio do cursor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    ''') # a tabela de usuários é criada aí
    conn.commit() #salva
    conn.close() #fecha
criar_banco()

#pagina inicial
@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='home.html')

#mostra o formulario de cadastro
@app.get('/cadastro', response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='cadastro.html')

#recebe dados do cadastro
@app.post('/cadastro', response_class=HTMLResponse)
def cadastro(
    request: Request, #dados do usuario
    email: str = Form(...), #obrigatorio
    nome: str = Form(...),
    senha: str = Form(...)
):
    conn = sqlite3.connect('usuario.db') 
    cursor = conn.cursor()

    #insere no banco
    cursor.execute(
        'INSERT INTO usuarios (email, nome, senha) VALUES (?, ?, ?)',
        (email, nome, senha)
    )

    #pega o id do usuario que acabou de criar
    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    #manda o id pro html
    return templates.TemplateResponse(
        request=request,
        name='resultado.html',
        context={'id': user_id})  #usa o id do usário

#pagina de perfil
@app.get('/perfil/{id}', response_class=HTMLResponse)
def perfil(request: Request, id: int):
    conn = sqlite3.connect('usuario.db')
    cursor = conn.cursor()

    #pega usuario pelo id
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
    usuario = cursor.fetchone()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name='perfil.html',
        context={'usuario': usuario})

#abrir editar
@app.get('/editar/{id}', response_class=HTMLResponse)
def editar_pagina(request: Request, id: int):
    conn = sqlite3.connect('usuario.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
    usuario = cursor.fetchone()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name='editar_usuario.html',
        context={'usuario': usuario})

#salvar edição
@app.post('/editar/{id}', response_class=HTMLResponse)
def editar(
    request: Request,
    id: int,
    email: str = Form(...),
    nome: str = Form(...),
    senha: str = Form(...)):

    conn = sqlite3.connect('usuario.db')
    cursor = conn.cursor()

    #atualiza só esse usuario
    cursor.execute(
        'UPDATE usuarios SET email = ?, nome = ?, senha = ? WHERE id = ?',
        (email, nome, senha, id))

    conn.commit()

    #pega atualizado
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
    usuario = cursor.fetchone()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name='perfil.html',
        context={'usuario': usuario})

#sair (leva pra home)
@app.get('/sair', response_class=HTMLResponse)
def sair(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='home.html')