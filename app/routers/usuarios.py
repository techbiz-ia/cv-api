from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import os

from app.database import SessionLocal
from app.models.usuarios import UsuarioModel, obtener_password_hash, verificar_password
from pydantic import BaseModel

router = APIRouter()

# 🔒 CONFIGURACIÓN DE SEGURIDAD JWT
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key_cambiar_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SCHEMAS
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

# 🔒 ENDPOINT 1: CREAR USUARIO
@router.post("/usuarios/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    db_user = db.query(UsuarioModel).filter(UsuarioModel.nombre == usuario.nombre).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    hashed_password = obtener_password_hash(usuario.password)
    
    nuevo_usuario = UsuarioModel(
        nombre=usuario.nombre,
        rol=usuario.rol,
        password=hashed_password
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# 🔒 ENDPOINT 2: LOGIN
@router.post("/usuarios/login", response_model=Token)
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == form_data.username).first()
    
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": usuario.nombre, "rol": usuario.rol, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}
@router.get("/usuarios/")
def obtener_todos_los_usuarios(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores pueden ver la lista de usuarios.")
    
    usuarios = db.query(UsuarioModel).all()
    resultado = []
    for usuario in usuarios:
        resultado.append({
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None
        })
    return resultado


@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores pueden eliminar usuarios.")
    
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario.nombre == payload.get("sub"):
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta.")
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario {usuario.nombre} eliminado exitosamente"}


@router.put("/usuarios/{usuario_id}/rol")
def cambiar_rol_usuario(usuario_id: int, nuevo_rol: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores pueden cambiar roles.")
    
    if nuevo_rol not in ["Admin", "User"]:
        raise HTTPException(status_code=400, detail="Rol inválido. Debe ser 'Admin' o 'User'.")
    
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.rol = nuevo_rol
    db.commit()
    return {"mensaje": f"Rol de {usuario.nombre} cambiado a {nuevo_rol}"}