from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer  # 🔒 1. Importar el esquema de seguridad
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json
from openai import OpenAI

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter()

# 🔒 2. Decirle a FastAPI dónde se obtiene el token (en el login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CVProcesarRequest(BaseModel):
    texto_cv: str

class CVUpdateRequest(BaseModel):
    texto_cv: str | None = None
    status: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 1. CREAR: Procesar CV con IA (OpenAI REAL)
# ---------------------------------------------------------
@router.post("/cvs/procesar-ia")
async def procesar_cv(
    request: CVProcesarRequest, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)  # 🔒 3. Exigir el token aquí (¡Esto hace aparecer el candado!)
):
    texto_original = request.texto_cv
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un experto en reclutamiento técnico. 
                    Tu tarea es extraer habilidades (skills) del texto del CV proporcionado.
                    Devuelve ÚNICAMENTE un objeto JSON válido con este formato exacto:
                    {
                      "skills": ["Habilidad 1", "Habilidad 2", "Habilidad 3"],
                      "texto_redactado": "Texto del CV con información personal redactada"
                    }
                    Si no encuentras habilidades, devuelve: {"skills": [], "texto_redactado": ""}
                    """
                },
                {
                    "role": "user", 
                    "content": texto_original
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        respuesta_ia = json.loads(result_text)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar con IA: {str(e)}"
        )

    nuevo_cv = CVDB(
        perfil_ciego_id=f"cv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        source_text=texto_original,
        redacted_text=respuesta_ia.get("texto_redactado", ""),
        status="procesado",
        redacted_count=max(0, len(texto_original) - len(respuesta_ia.get("texto_redactado", "")))
    )
    db.add(nuevo_cv)
    db.flush()

    for skill_nombre in respuesta_ia.get("skills", []):
        db.add(SkillDB(skill=skill_nombre, cv_id=nuevo_cv.id))

    db.commit()
    db.refresh(nuevo_cv)

    return {
        "mensaje": "CV procesado y guardado con IA real", 
        "cv_id": nuevo_cv.id, 
        "skills_extraidas": respuesta_ia.get("skills", [])
    }

# ---------------------------------------------------------
# 2. LEER: Obtener todos los CVs
# ---------------------------------------------------------
@router.get("/cvs/")
def obtener_todos_los_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CVDB).all()
    resultado = []
    for cv in cvs:
        skills = db.query(SkillDB).filter(SkillDB.cv_id == cv.id).all()
        resultado.append({
            "id": cv.id,
            "perfil_ciego_id": cv.perfil_ciego_id,
            "texto_original": cv.source_text,
            "texto_redactado": cv.redacted_text,
            "status": cv.status,
            "skills": [s.skill for s in skills]
        })
    return resultado

# ---------------------------------------------------------
# 3. ACTUALIZAR: Modificar un CV existente (PUT)
# ---------------------------------------------------------
@router.put("/cvs/{cv_id}")
def actualizar_cv(cv_id: int, request: CVUpdateRequest, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    if request.texto_cv is not None:
        cv.source_text = request.texto_cv
    if request.status is not None:
        cv.status = request.status

    db.commit()
    db.refresh(cv)
    return {"mensaje": "CV actualizado exitosamente", "cv": cv.id}

# ---------------------------------------------------------
# 4. ELIMINAR: Borrar un CV y sus skills asociadas (DELETE)
# ---------------------------------------------------------
@router.delete("/cvs/{cv_id}")
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    db.delete(cv)
    db.commit()
    return {"mensaje": f"CV {cv_id} y sus habilidades asociadas eliminados exitosamente"}
