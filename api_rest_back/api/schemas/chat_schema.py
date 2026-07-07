from typing import List, Optional

from pydantic import BaseModel

from api.utils.enums import TipoAcao

class ChatRequest(BaseModel):
    prompt: str
    
class ChatRequestPersonalizado(BaseModel):
    message: str
    interesses_list: List[str]
    apelido: str
    disciplina: str
    mode: TipoAcao
    topicos: str = ""
    nome_mascote: str = ""
    personalidade_mascote: str = ""
    tipo_mascote: str = ""
    linguagem_mascote: str = ""
    estado_mascote: str = ""

class ChatResponse(BaseModel):
    response: str

    class Config:
        from_attributes = True


class VisualContent(BaseModel):
    mindmap: Optional[str] = None
    flashcards: Optional[List[dict]] = None
    chart: Optional[dict] = None
    mermaid: Optional[str] = None


class ResumoResponse(BaseModel):
    tipo: str = "resumo"
    titulo: str
    resumo: str
    sugestoes: list[str]
    visual: Optional[VisualContent] = None


class Alternativa(BaseModel):
    letra: str
    texto: str


class QuestaoExercicio(BaseModel):
    pergunta: str
    alternativas: list[Alternativa]
    resposta_correta: str


class AvaliacaoResponse(BaseModel):
    tipo: str = "exercicio"
    titulo: str
    questoes: list[QuestaoExercicio]
    sugestoes: list[str]
    visual: Optional[VisualContent] = None


class QuestaoQuiz(BaseModel):
    pergunta: str
    alternativas: list[str]
    resposta: Optional[str] = None


class QuizResponse(BaseModel):
    tipo: str = "quiz"
    titulo: str
    perguntas: list[QuestaoQuiz]
    sugestoes: list[str]
    visual: Optional[VisualContent] = None


class ItemCronograma(BaseModel):
    dia: str
    assunto: str
    descricao: Optional[str] = None


class RevisaoResponse(BaseModel):
    tipo: str = "revisao"
    titulo: str
    cronograma: list[ItemCronograma]
    sugestoes: list[str]
    visual: Optional[VisualContent] = None
    
    