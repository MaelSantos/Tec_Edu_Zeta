from typing import Optional, List
from pydantic import BaseModel


class DisciplinaCreate(BaseModel):
    nome: str
    dificuldade: str

    class Config:
        from_attributes = True


class DisciplinaResponse(BaseModel):
    id: int
    nome: str
    dificuldade: str

    class Config:
        from_attributes = True


class DisciplinaWithConteudos(DisciplinaResponse):
    conteudos: List["ConteudoResponse"] = []

    class Config:
        from_attributes = True
