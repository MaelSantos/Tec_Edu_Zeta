from enum import Enum
from api.util.enums import TipoDificuldade


class Disciplina():
    nome: NomesDisciplinas
    dificuldade: TipoDificuldade
    
    
class NomesDisciplinas(Enum):
    PORTUGUES = "Português"
    MATEMATICA = "Matemática"
    CIENCIAS = "Ciências"
    HISTORIA = "História"
    GEOGRAFIA = "Geografia"
    ARTES = "Artes"
    INGLES = "Inglês"
    EDUCACAO_FISICA = "Educação física"
    TEMAS_INTERDISCIPLINARES = "Temas interdisciplinares e projetos escolares"