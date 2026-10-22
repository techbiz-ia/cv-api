from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class CVCreate(BaseModel):
    cv_texto: str = Field(..., min_length=1)
    habilidades_tecnicas: List[str] = []

class CVRead(BaseModel):
    id: int
    perfil_ciego_id: str
    source_text: str
    redacted_text: Optional[str] = None
    status: str
    redacted_count: int
    habilidades_tecnicas: List[str] = []

    class Config:
        from_attributes = True
