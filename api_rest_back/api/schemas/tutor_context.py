from dataclasses import dataclass

@dataclass
class TutorContext:
    aluno_id: int
    apelido: str
    disciplina: str
    topicos: str
    interesses: list[str]
    mascote: str
