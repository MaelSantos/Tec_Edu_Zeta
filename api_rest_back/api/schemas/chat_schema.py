from typing import List

from pydantic import BaseModel

from api.schemas.exercicio_schema import ExercicioResponse
from api.utils.enums import TipoAcao

class ChatRequest(BaseModel):
    prompt: str
    
class ChatRequestPersonalizado(BaseModel):
    message: str
    interesses_list: List[str]
    apelido: str
    disciplina: str
    mode: TipoAcao

class ChatResponse(BaseModel):
    response: str

    class Config:
        from_attributes = True


# melhorar...
class ResumoResponse(BaseModel):
    tipo: str
    titulo: str
    resumo: str

class AvaliacaoResponse(BaseModel):
    tipo: str
    titulo: str
    exercicios: list[ExercicioResponse]

class QuizResponse(BaseModel):
    tipo: str
    perguntas: list

class RevisaoResponse(BaseModel):
    tipo: str
    cronograma: list