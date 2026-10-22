from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.database import SessionLocal
from app.models.usuarios import UsuarioModel, verificar_password, obtener_password_hash
from app.schemas.usuarios import Token, UsuarioCrear, UsuarioResponse, UsuarioUpdate

router = APIRouter()

SECRET_KEY = "clave_secreta_de_desarrollo_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except JWTError:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    user = db.query(UsuarioModel).filter(UsuarioModel.nombre == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

@router.post("/usuarios/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == form_data.username).first()
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": usuario.nombre, "rol": usuario.rol})
    return {"access_token": access_token, "token_type": "bearer"}

# ¡ESTE ENDPOINT ES PÚBLICO! (No tiene current_user)
@router.post("/usuarios/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.nombre == usuario.nombre).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    nuevo_usuario = UsuarioModel(
        nombre=usuario.nombre,
        rol=usuario.rol,
        password=obtener_password_hash(usuario.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# ESTOS SÍ ESTÁN PROTEGIDOS
@router.get("/usuarios/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    return db.query(UsuarioModel).all()

@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.patch("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(usuario_id: int, usuario_update: UsuarioUpdate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario_update.nombre is not None:
        usuario.nombre = usuario_update.nombre
    if usuario_update.rol is not None:
        usuario.rol = usuario_update.rol
    if usuario_update.password is not None:
        usuario.password = obtener_password_hash(usuario_update.password)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado exitosamente"}
