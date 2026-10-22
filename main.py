from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import usuarios, cvs

# Importar modelos para que SQLAlchemy los registre antes de crear tablas
import app.models.usuarios
import app.models.cv

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos verificadas y creadas.")
    yield

# Aquí está la clave: FastAPI crea /docs y /redoc por defecto
app = FastAPI(
    title="Mi API MVP", 
    version="0.1.0", 
    lifespan=lifespan,
    docs_url="/docs",      # Forzamos la ruta de la documentación
    redoc_url="/redoc"     # Forzamos la ruta alternativa
)

app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/")
def read_root():
    return {"mensaje": "API MVP funcionando correctamente"}

@app.get("/health")
def health():
    return {"status": "ok"}
