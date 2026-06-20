from enum import Enum
from api.model.disciplina_model import Disciplina
from api.util.enums import TipoDificuldade

class Conteudo():
    nome: str
    descricao: str
    dificuldade: TipoDificuldade
    disciplina: Disciplina
    
