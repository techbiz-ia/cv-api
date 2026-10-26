from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import usuarios, cvs

import app.models.usuarios
import app.models.cv

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos verificadas y creadas.")
    yield

app = FastAPI(
    title="Mi API MVP", 
    version="0.1.0", 
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(cvs.router)

@app.get("/")
def read_root():
    return {"mensaje": "API MVP funcionando correctamente"}

@app.get("/health")
def health():
    return {"status": "ok"}

