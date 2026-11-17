from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(String, default="User")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    acepto_terminos = Column(Boolean, default=False) # ← Campo agregado