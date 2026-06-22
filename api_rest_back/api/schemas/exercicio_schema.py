from typing import Optional, List
from pydantic import BaseModel


class ExercicioCreate(BaseModel):
    nome: str
    dificuldade: str
    exemplo: Optional[str] = None
    conteudo_id: int

    class Config:
        from_attributes = True


class ExercicioResponse(BaseModel):
    id: int
    nome: str
    dificuldade: str
    exemplo: Optional[str] = None
    conteudo_id: int

    class Config:
        from_attributes = True


class ExercicioWithQuestoes(ExercicioResponse):
    questoes: List["QuestaoResponse"] = []

    class Config:
        from_attributes = True
