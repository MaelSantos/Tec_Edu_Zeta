from typing import Optional
from pydantic import BaseModel


class AlunoCreate(BaseModel):
    """Schema para criação de um novo Aluno."""
    apelido: str
    mascote_id: Optional[int] = None

    class Config:
        from_attributes = True


class AlunoUpdate(BaseModel):
    """Schema para atualização de um Aluno."""
    apelido: Optional[str] = None
    mascote_id: Optional[int] = None

    class Config:
        from_attributes = True


class AlunoResponse(BaseModel):
    """Schema para resposta de Aluno (serialização)."""
    id: int
    apelido: str
    mascote_id: Optional[int] = None

    class Config:
        from_attributes = True


class DisciplinaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class InteresseResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class DesempenhoResponse(BaseModel):
    id: int
    nota_media: Optional[float] = None
    total_exercicios: Optional[int] = None

    class Config:
        from_attributes = True


class MascoteResponse(BaseModel):
    id: int
    tipo: Optional[str] = None
    nivel: Optional[int] = None

    class Config:
        from_attributes = True


class AlunoWithDisciplinas(AlunoResponse):
    disciplinas: list[DisciplinaResponse] = []

    class Config:
        from_attributes = True


class AlunoWithInteresses(AlunoResponse):
    interesses: list[InteresseResponse] = []

    class Config:
        from_attributes = True


class AlunoWithDesempenhos(AlunoResponse):
    desempenhos: list[DesempenhoResponse] = []

    class Config:
        from_attributes = True


class AlunoWithMascote(AlunoResponse):
    mascote: Optional[MascoteResponse] = None

    class Config:
        from_attributes = True
