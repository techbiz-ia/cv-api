from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os

from app.database import SessionLocal
# ⚠️ CAMBIA 'UsuarioDB' POR EL NOMBRE REAL DE TU CLASE EN app/models/usuarios.py
from app.models.usuarios import UsuarioDB 
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------
# 🔒 CONFIGURACIÓN DE SEGURIDAD
# ---------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key_cambiar_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# SCHEMAS
# ---------------------------------------------------------
class UsuarioCrear(BaseModel):
    nombre: str
    rol: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    rol: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------------------------------------------------------
# 🔒 ENDPOINT 1: CREAR USUARIO
# ---------------------------------------------------------
@router.post("/usuarios/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    # ⚠️ Asegúrate de que 'UsuarioDB' coincida con tu modelo real
    db_user = db.query(UsuarioDB).filter(UsuarioDB.nombre == usuario.nombre).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    hashed_password = get_password_hash(usuario.password)

    nuevo_usuario = UsuarioDB(
        nombre=usuario.nombre,
        rol=usuario.rol,
        password=hashed_password
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# ---------------------------------------------------------
# 🔒 ENDPOINT 2: LOGIN
# ---------------------------------------------------------
@router.post("/usuarios/login", response_model=Token)
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.nombre == form_data.username).first()
    
    if not usuario or not verify_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": usuario.nombre, "rol": usuario.rol, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}
