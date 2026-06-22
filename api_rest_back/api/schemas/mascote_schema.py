from typing import Optional
from pydantic import BaseModel


class MascoteCreate(BaseModel):
    nome: str
    personalidade: str
    tipo: str
    estado: str
    linguagem: str

    class Config:
        from_attributes = True


class MascoteResponse(BaseModel):
    id: int
    nome: str
    personalidade: str
    tipo: str
    estado: str
    linguagem: str

    class Config:
        from_attributes = True
