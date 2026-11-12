from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import json
from datetime import datetime
from openai import OpenAI

from app.database import SessionLocal
from app.models.cv import CVDB, SkillDB

router = APIRouter(prefix="/cvs", tags=["CVs"])

# Carpeta donde se guardarán los archivos PDF originales
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProcesarIARequest(BaseModel):
    texto_cv: str
    whatsapp: str = ""
    archivo_pdf: str = None

def analizar_con_ia(texto: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Falta la clave de API de OpenAI en el servidor.")
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Analiza el siguiente texto de un currículum vitae para un sistema de Blind Hiring.
    1. Extrae las habilidades técnicas y blandas principales como una lista de strings.
    2. Redacta un resumen profesional breve (máximo 3 oraciones).
    3. REDACTA (reemplaza con [REDACTADO]) cualquier dato sensible como correos electrónicos, números de teléfono, direcciones exactas o DNI, pero mantén el nombre y las habilidades intactas.
    
    Responde ÚNICAMENTE con un objeto JSON válido en este formato exacto:
    {{
      "habilidades": ["Habilidad 1", "Habilidad 2"],
      "resumen_redactado": "Texto del resumen con datos sensibles redactados."
    }}
    
    Texto del CV:
    {texto}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar con IA: {str(e)}")

@router.post("/procesar-ia", status_code=201)
def procesar_ia(request: ProcesarIARequest, db: Session = Depends(get_db)):
    if not request.texto_cv.strip():
        raise HTTPException(status_code=400, detail="El texto del CV no puede estar vacío.")
    
    resultado_ia = analizar_con_ia(request.texto_cv)
    perfil_ciego_id = f"cv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    nuevo_cv = CVDB(
        perfil_ciego_id=perfil_ciego_id,
        source_text="Texto pegado manualmente", # Optimizado: no guardamos el texto gigante
        redacted_text=resultado_ia.get("resumen_redactado", "Resumen generado por IA"),
        status="procesado",
        whatsapp=request.whatsapp or None,
        archivo_pdf=request.archivo_pdf # Será None si es texto pegado
    )
    db.add(nuevo_cv)
    db.flush()
    
    habilidades = resultado_ia.get("habilidades", [])
    for skill_name in habilidades:
        skill = SkillDB(skill=skill_name, cv_id=nuevo_cv.id)
        db.add(skill)
    
    db.commit()
    db.refresh(nuevo_cv)
    
    return {
        "status": "procesado",
        "perfil_ciego_id": nuevo_cv.perfil_ciego_id,
        "skills_extraidas": habilidades,
        "texto_redactado": nuevo_cv.redacted_text
    }

@router.post("/procesar-archivo", status_code=201)
async def procesar_archivo(
    file: UploadFile = File(...),
    whatsapp: str = Form(""),
    db: Session = Depends(get_db)
):
    filename = file.filename.lower() if file.filename else ""
    if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .pdf, .docx o .txt")
    
    # 1. Guardar el archivo físico con nombre único para evitar colisiones
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    contenido_bytes = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(contenido_bytes)
    
    # 2. Extraer texto temporalmente SOLO para que la IA lo analice
    contenido = ""
    try:
        if filename.endswith('.txt'):
            contenido = contenido_bytes.decode("utf-8")
        elif filename.endswith('.pdf'):
            import PyPDF2
            import io
            reader = PyPDF2.PdfReader(io.BytesIO(contenido_bytes))
            for page in reader.pages:
                contenido += page.extract_text() + "\n"
        elif filename.endswith('.docx'):
            import docx
            import io
            doc = docx.Document(io.BytesIO(contenido_bytes))
            contenido = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")
    
    if not contenido.strip():
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del archivo.")
    
    # 3. Analizar con IA y guardar en BD de forma optimizada
    request = ProcesarIARequest(texto_cv=contenido, whatsapp=whatsapp, archivo_pdf=unique_filename)
    
    resultado_ia = analizar_con_ia(request.texto_cv)
    perfil_ciego_id = f"cv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    nuevo_cv = CVDB(
        perfil_ciego_id=perfil_ciego_id,
        source_text=f"Archivo: {unique_filename}", # Optimizado: solo guardamos la referencia
        redacted_text=resultado_ia.get("resumen_redactado", "Resumen generado por IA"),
        status="procesado",
        whatsapp=request.whatsapp or None,
        archivo_pdf=unique_filename # <-- Aquí guardamos el nombre del archivo PDF
    )
    db.add(nuevo_cv)
    db.flush()
    
    habilidades = resultado_ia.get("habilidades", [])
    for skill_name in habilidades:
        skill = SkillDB(skill=skill_name, cv_id=nuevo_cv.id)
        db.add(skill)
    
    db.commit()
    db.refresh(nuevo_cv)
    
    return {
        "status": "procesado",
        "perfil_ciego_id": nuevo_cv.perfil_ciego_id,
        "skills_extraidas": habilidades,
        "texto_redactado": nuevo_cv.redacted_text
    }

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
            "experiencia_resumen": cv.redacted_text or cv.source_text or "Sin resumen disponible",
            "archivo_pdf": cv.archivo_pdf # <-- Agregado para que el frontend sepa que existe el archivo
        })

    return {"total": len(resultado), "cvs": resultado}

@router.delete("/{cv_id}", status_code=200)
def eliminar_cv(cv_id: int, db: Session = Depends(get_db)):
    cv = db.query(CVDB).filter(CVDB.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    # Opcional: Eliminar también el archivo físico para limpiar espacio
    if cv.archivo_pdf:
        file_path = os.path.join(UPLOAD_DIR, cv.archivo_pdf)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(cv)
    db.commit()
    return {"mensaje": "CV eliminado correctamente", "id_eliminado": cv_id}