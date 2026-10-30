from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
from passlib.context import CryptContext

from app.database import SessionLocal
from app.models.usuarios import UsuarioModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key_cambiar_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validar_token_y_obtener_rol(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")
    return payload

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class UsuarioCrear(BaseModel):
    nombre: str
    password: str
    rol: str = "User"

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/usuarios/", status_code=201)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == usuario.nombre).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El usuario ya existe.")
    
    hashed_password = pwd_context.hash(usuario.password)
    nuevo_usuario = UsuarioModel(nombre=usuario.nombre, password=hashed_password, rol=usuario.rol)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"id": nuevo_usuario.id, "nombre": nuevo_usuario.nombre, "rol": nuevo_usuario.rol}

@router.post("/usuarios/login", response_model=Token)
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == form_data.username).first()
    if not usuario or not pwd_context.verify(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    
    access_token = crear_token(data={"sub": usuario.nombre, "rol": usuario.rol})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# NUEVOS ENDPOINTS DE GESTIÓN DE USUARIOS
# ==========================================

@router.get("/usuarios/")
def obtener_todos_los_usuarios(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores pueden ver la lista de usuarios.")
    
    usuarios = db.query(UsuarioModel).all()
    resultado = []
    for usuario in usuarios:
        fecha = getattr(usuario, 'fecha_creacion', None)
        resultado.append({
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "fecha_creacion": fecha.isoformat() if fecha else None
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