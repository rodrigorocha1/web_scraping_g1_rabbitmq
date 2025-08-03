from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import hashlib
import uuid

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Dataclass com id_noticia recebido no input
@dataclass
class Noticia:
    id_noticia: str
    titulo: str
    subtitulo: str
    texto: str
    autor: str
    data_hora: Optional[datetime]

DATABASE_URL = "sqlite:///./noticias.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SESSOES_ATIVAS = {}

def gerar_hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return gerar_hash_senha(senha) == senha_hash

def obter_token(authorization: str = Header(..., alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.strip()
    if token not in SESSOES_ATIVAS:
        raise HTTPException(status_code=401, detail="Token inválido")
    return token

class NoticiaDB(Base):
    __tablename__ = "noticias"
    id_noticia = Column(String(500), primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    subtitulo = Column(String(255), nullable=True)
    texto = Column(Text, nullable=False)
    autor = Column(String(100), nullable=True)
    data_hora = Column(DateTime, nullable=False)

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(128), nullable=False)

Base.metadata.create_all(bind=engine)

# Agora inclui id_noticia no input
class NoticiaInput(BaseModel):
    id_noticia: str
    titulo: str
    subtitulo: Optional[str] = None
    texto: str
    autor: Optional[str] = None
    data_hora: Optional[datetime] = None

class UsuarioInput(BaseModel):
    username: str
    senha: str

class NoticiaResponse(BaseModel):
    id_noticia: str
    titulo: str
    subtitulo: Optional[str]
    texto: str
    autor: Optional[str]
    data_hora: datetime

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    message: str
    username: str
    token: str

app = FastAPI(title="API de Notícias com Token Correto no Header", version="2.2.0")

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except OperationalError:
        raise HTTPException(status_code=500, detail="Falha na conexão com o banco")

@app.post("/usuarios")
def criar_usuario(usuario: UsuarioInput):
    db = SessionLocal()
    try:
        if db.query(UsuarioDB).filter_by(username=usuario.username).first():
            raise HTTPException(status_code=400, detail="Usuário já existe")
        novo_usuario = UsuarioDB(username=usuario.username, senha_hash=gerar_hash_senha(usuario.senha))
        db.add(novo_usuario)
        db.commit()
        return {"message": "Usuário criado", "username": usuario.username}
    finally:
        db.close()

@app.post("/login", response_model=LoginResponse)
def login(usuario: UsuarioInput):
    db = SessionLocal()
    try:
        user_db = db.query(UsuarioDB).filter_by(username=usuario.username).first()
        if not user_db or not verificar_senha(usuario.senha, user_db.senha_hash):
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
        token = str(uuid.uuid4())
        SESSOES_ATIVAS[token] = usuario.username
        return {"message": "Login ok", "username": usuario.username, "token": token}
    finally:
        db.close()

@app.post("/noticias", response_model=NoticiaResponse)
def criar_noticia(noticia: NoticiaInput, token: str = Depends(obter_token)):
    db = SessionLocal()
    try:
        if db.query(NoticiaDB).filter_by(id_noticia=noticia.id_noticia).first():
            raise HTTPException(status_code=400, detail="Notícia já cadastrada")

        noticia_obj = Noticia(
            id_noticia=noticia.id_noticia,
            titulo=noticia.titulo,
            subtitulo=noticia.subtitulo or "",
            texto=noticia.texto,
            autor=noticia.autor or "Desconhecido",
            data_hora=noticia.data_hora or datetime.now()
        )

        nova_noticia = NoticiaDB(
            id_noticia=noticia_obj.id_noticia,
            titulo=noticia_obj.titulo,
            subtitulo=noticia_obj.subtitulo,
            texto=noticia_obj.texto,
            autor=noticia_obj.autor,
            data_hora=noticia_obj.data_hora
        )

        db.add(nova_noticia)
        db.commit()
        db.refresh(nova_noticia)
        return nova_noticia
    finally:
        db.close()

@app.get("/noticias", response_model=List[NoticiaResponse])
def listar_noticias(skip: int = 0, limit: int = 10, token: str = Depends(obter_token)):
    db = SessionLocal()
    try:
        return db.query(NoticiaDB).offset(skip).limit(limit).all()
    finally:
        db.close()

@app.get("/noticias/{id_noticia}", response_model=NoticiaResponse)
def buscar_noticia(id_noticia: str, token: str = Depends(obter_token)):
    db = SessionLocal()
    try:
        noticia = db.query(NoticiaDB).filter_by(id_noticia=id_noticia).first()
        if not noticia:
            raise HTTPException(status_code=404, detail="Notícia não encontrada")
        return noticia
    finally:
        db.close()
