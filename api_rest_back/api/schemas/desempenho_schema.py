from typing import Optional
from pydantic import BaseModel


class DesempenhoCreate(BaseModel):
    tempo_de_estudo: int
    acertos: int
    erros: int
    aluno_id: int
    disciplina_id: int

    class Config:
        from_attributes = True


class DesempenhoResponse(BaseModel):
    id: int
    tempo_de_estudo: int
    acertos: int
    erros: int
    aluno_id: int
    disciplina_id: int

    class Config:
        from_attributes = True
