from enum import Enum


class TipoDificuldade(Enum):
    FACIL = "Fácil"
    MEDIO = "Médio"
    DIFICIL = "Difícil"

class TipoAcao(Enum):
    RESUMO = "Resumo"
    EXERCICIO = "Exercício"
    REVISAO = "Revisão"
    QUIZ = "Quiz"