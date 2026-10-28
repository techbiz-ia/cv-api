from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class CVDB(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    perfil_ciego_id = Column(String, unique=True, index=True)
    source_text = Column(Text)
    redacted_text = Column(Text)
    status = Column(String, default="pendiente")
    redacted_count = Column(Integer, default=0)
    whatsapp = Column(String, nullable=True)  # Número de WhatsApp del candidato (opcional)
    
    skills = relationship("SkillDB", back_populates="cv", cascade="all, delete-orphan")

class SkillDB(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"))
    
    cv = relationship("CVDB", back_populates="skills")

# NOTA: No hay create_all aquí. Se hace en main.py
