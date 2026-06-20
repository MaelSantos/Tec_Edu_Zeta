from api.model.aluno_model import Aluno
from api.model.disciplina_model import Disciplina


class Desempenho():
    tempo_de_estudo: int #em minutos
    acertos: int
    erros: int
    aluno_id: Aluno
    disciplina_id: Disciplina