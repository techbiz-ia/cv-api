from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter(prefix="/cvs", tags=["CVs"])

# Definimos get_db localmente, exactamente como en usuarios.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/lista")
def listar_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CVDB).all()
    resultado = []
    
    for cv in cvs:
        habilidades = [s.skill for s in cv.skills] if cv.skills else []
        
        resultado.append({
            "id": cv.id,
            "nombre_completo": cv.perfil_ciego_id or "Nombre no disponible",
            "whatsapp": cv.whatsapp,
            "email": None,
            "status": cv.status,
            "habilidades": habilidades,
            "experiencia_resumen": cv.redacted_text or cv.source_text or "Sin resumen disponible"
        })
        
    return {"total": len(resultado), "cvs": resultado}

@router.delete("/{cv_id}", status_code=200)
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")
    
    db.delete(cv)
    db.commit()
    return {"mensaje": "CV eliminado correctamente", "id_eliminado": cv_id}