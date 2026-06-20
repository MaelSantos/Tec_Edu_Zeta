from api.model.questao_model import Questao
from api.model.conteudo_model import Conteudo
from api.util.enums import TipoDificuldade

class Exercicio():
    nome: str
    dificuldade: TipoDificuldade
    exemplo: str
    conteudo: Conteudo
    questoes: list[Questao]
    # revisao_id(s?)
