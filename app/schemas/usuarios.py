from typing import Optional
from pydantic import BaseModel, Field

class UsuarioCrear(BaseModel):
    nombre: str
    rol: str = "User"
    password: str = Field(..., min_length=6)

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    rol: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
