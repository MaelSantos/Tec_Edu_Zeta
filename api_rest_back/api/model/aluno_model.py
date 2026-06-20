from api.model.mascote_model import Mascote
from api.model.disciplina_model import Disciplina
from model.interesse_model import Interesse


class Aluno():
    nome: str
    idade: int
    interesses: list[Interesse]
    disciplinas: list[Disciplina]
    mascote: Mascote
    
    