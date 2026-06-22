from typing import Optional
from pydantic import BaseModel


class QuestaoCreate(BaseModel):
    enunciado: str
    dica: Optional[str] = None
    resposta_correta: str
    resposta_incorreta1: Optional[str] = None
    resposta_incorreta2: Optional[str] = None
    resposta_incorreta3: Optional[str] = None
    resposta_incorreta4: Optional[str] = None
    exercicio_id: int

    class Config:
        from_attributes = True


class QuestaoResponse(BaseModel):
    id: int
    enunciado: str
    dica: Optional[str] = None
    resposta_correta: str
    resposta_incorreta1: Optional[str] = None
    resposta_incorreta2: Optional[str] = None
    resposta_incorreta3: Optional[str] = None
    resposta_incorreta4: Optional[str] = None
    exercicio_id: int

    class Config:
        from_attributes = True
