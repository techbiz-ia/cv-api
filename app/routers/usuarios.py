from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import os

from app.database import SessionLocal
# ✅ IMPORTAMOS EL NOMBRE REAL DE TU MODELO Y SUS FUNCIONES
from app.models.usuarios import UsuarioModel, obtener_password_hash, verificar_password
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------
# 🔒 CONFIGURACIÓN DE SEGURIDAD JWT
# ---------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key_cambiar_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# SCHEMAS (Pydantic)
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
# 🔒 ENDPOINT 1: CREAR USUARIO (CONTRASEÑA ENCRIPTADA)
# ---------------------------------------------------------
@router.post("/usuarios/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    # ✅ Usamos UsuarioModel
    db_user = db.query(UsuarioModel).filter(UsuarioModel.nombre == usuario.nombre).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    # ✅ Usamos tu función de encriptación del modelo
    hashed_password = obtener_password_hash(usuario.password)

    # ✅ Creamos la instancia con UsuarioModel
    nuevo_usuario = UsuarioModel(
        nombre=usuario.nombre,
        rol=usuario.rol,
        password=hashed_password
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# ---------------------------------------------------------
# 🔒 ENDPOINT 2: LOGIN (VERIFICACIÓN SEGURA)
# ---------------------------------------------------------
@router.post("/usuarios/login", response_model=Token)
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ✅ Buscamos usando UsuarioModel
    usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == form_data.username).first()
    
    # ✅ Verificamos con tu función del modelo
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": usuario.nombre, "rol": usuario.rol, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}
