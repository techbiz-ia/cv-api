from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
from passlib.context import CryptContext

from app.database import SessionLocal
from app.models.usuarios import User # ← Importamos el modelo correcto

router = APIRouter(prefix="/usuarios", tags=["Usuarios"]) # ← Agregado prefix para que coincida con el frontend

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

# ✅ MODELO ACTUALIZADO CON EL CAMPO DE TÉRMINOS
class UsuarioCrear(BaseModel):
    nombre: str
    password: str
    rol: str = "User"
    acepto_terminos: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/", status_code=201)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    # 1. Validar que aceptó los términos
    if not usuario.acepto_terminos:
        raise HTTPException(status_code=400, detail="Debes aceptar las políticas de privacidad y términos de uso.")
    
    # 2. Verificar si existe (usando User, no UsuarioModel)
    db_usuario = db.query(User).filter(User.nombre == usuario.nombre).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El usuario ya existe.")
    
    # 3. Crear usuario con todos los campos
    hashed_password = pwd_context.hash(usuario.password)
    nuevo_usuario = User(
        nombre=usuario.nombre, 
        password=hashed_password, 
        rol=usuario.rol,
        acepto_terminos=usuario.acepto_terminos # ← Guardamos la aceptación
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {"mensaje": "Usuario creado exitosamente", "id": nuevo_usuario.id}

@router.post("/login", response_model=Token)
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Usando User en lugar de UsuarioModel
    usuario = db.query(User).filter(User.nombre == form_data.username).first()
    if not usuario or not pwd_context.verify(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    
    access_token = crear_token(data={"sub": usuario.nombre, "rol": usuario.rol})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/")
def obtener_todos_los_usuarios(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    
    usuarios = db.query(User).all()
    return [{
        "id": u.id, 
        "nombre": u.nombre, 
        "rol": u.rol, 
        "fecha_creacion": u.fecha_creacion.isoformat() if u.fecha_creacion else None
    } for u in usuarios]

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.nombre == payload.get("sub"):
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta.")
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario {usuario.nombre} eliminado exitosamente"}

@router.put("/{usuario_id}/rol")
def cambiar_rol_usuario(usuario_id: int, nuevo_rol: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = validar_token_y_obtener_rol(token)
    if payload.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    if nuevo_rol not in ["Admin", "User"]:
        raise HTTPException(status_code=400, detail="Rol inválido.")
    
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.rol = nuevo_rol
    db.commit()
    return {"mensaje": f"Rol de {usuario.nombre} cambiado a {nuevo_rol}"}
from fastapi.responses import HTMLResponse

@router.get("/politicas", response_class=HTMLResponse)
def mostrar_politicas():
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Políticas de Privacidad - Nexus Inclusivo</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0a0a0f 0%,#1a1a2e 50%,#0f0f1e 100%);color:#e2e8f0;min-height:100vh;padding:40px 20px}
.container{max-width:800px;margin:0 auto;background:rgba(30,41,59,0.7);backdrop-filter:blur(20px);border:2px solid rgba(99,102,241,0.2);border-radius:20px;padding:40px}
h1{font-size:32px;font-weight:900;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:20px}
h2{font-size:22px;font-weight:700;color:#818cf8;margin:30px 0 15px}
p,li{font-size:15px;line-height:1.8;color:#cbd5e1;margin-bottom:12px}
ul{margin:15px 0;padding-left:25px}
.back-btn{display:inline-block;margin-top:30px;padding:12px 24px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-decoration:none;border-radius:12px;font-weight:700}
</style>
</head>
<body>
<div class="container">
<h1>Políticas de Privacidad y Términos de Uso</h1>
<p><strong>Última actualización:</strong> 17 de noviembre de 2026</p>
<h2>1. Introducción</h2>
<p>Nexus Inclusivo es un sistema de reclutamiento ético potenciado por Inteligencia Artificial que opera bajo el modelo de Blind Hiring.</p>
<h2>2. Datos que Recopilamos</h2>
<ul>
<li><strong>Datos de registro:</strong> Nombre de usuario y contraseña (encriptada).</li>
<li><strong>Información del CV:</strong> Habilidades, experiencia profesional y resumen redactado por IA.</li>
<li><strong>Datos de contacto opcionales:</strong> Número de WhatsApp.</li>
</ul>
<p><strong>NO recopilamos:</strong> Nombre completo, género, edad, foto, dirección, ni ningún dato que pueda revelar tu identidad durante el proceso de Blind Hiring.</p>
<h2>3. Blind Hiring y Privacidad</h2>
<p>Las empresas solo ven tu perfil profesional redactado por IA. Tu identidad solo se revela si tú lo autorizas explícitamente.</p>
<h2>4. Tus Derechos</h2>
<ul>
<li>Acceder a tus datos en cualquier momento.</li>
<li>Solicitar la eliminación completa de tu perfil.</li>
<li>No ser discriminado por género, edad, etnia u otro factor.</li>
</ul>
<h2>5. Contacto</h2>
<p>WhatsApp: +54 9 299 329 3669</p>
<a href="/" class="back-btn">← Volver al inicio</a>
</div>
</body>
</html>"""