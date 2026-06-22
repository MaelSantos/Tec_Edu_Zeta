from typing import Optional, List
from pydantic import BaseModel


class ConteudoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    dificuldade: str
    disciplina_id: int

    class Config:
        from_attributes = True


class ConteudoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    dificuldade: str
    disciplina_id: int

    class Config:
        from_attributes = True


class ConteudoWithExercicios(ConteudoResponse):
    exercicios: List["ExercicioResponse"] = []
    revisoes: List["RevisaoResponse"] = []

    class Config:
        from_attributes = True
