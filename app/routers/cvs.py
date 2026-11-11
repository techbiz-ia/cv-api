from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.database import SessionLocal
from app.models.cv import CV

router = APIRouter(prefix="/cvs", tags=["CVs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/lista")
def listar_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CV).all()
    resultado = []
    for cv in cvs:
        habilidades = []
        if cv.habilidades:
            try:
                habilidades = json.loads(cv.habilidades) if isinstance(cv.habilidades, str) else cv.habilidades
            except Exception:
                habilidades = [str(cv.habilidades)]
        
        resultado.append({
            "id": cv.id,
            "nombre": cv.nombre,
            "email": cv.email,
            "telefono": cv.telefono,
            "puesto_buscado": cv.puesto_buscado,
            "estado": cv.estado,
            "habilidades": habilidades,
            "resumen_profesional": cv.resumen_profesional
        })
    return {"total": len(resultado), "cvs": resultado}

# --- ÚNICO AGREGADO: Endpoint para eliminar ---
@router.delete("/{cv_id}", status_code=200)
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")
    db.delete(cv)
    db.commit()
    return {"mensaje": "CV eliminado correctamente", "id_eliminado": cv_id}