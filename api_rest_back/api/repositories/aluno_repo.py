from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models.aluno_model import Aluno
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException
from api.repositories.database import session

class AlunoRepo(BaseRepo):
    """Repositório para operações de banco sobre a entidade Aluno.

    Inclui métodos que usam eager-loading para evitar problema de N+1 quando
    o endpoint precisa carregar relações com o `Aluno`. 
    Evita que o endpoint precise fazer múltiplas consultas para carregar as relações do aluno, 
    melhorando a performance.
    """

    def get_by_username(self, username: str) -> Optional[Aluno]:
        try:
            return session.query(Aluno).filter(Aluno.apelido == username).first()
        except Exception:
            raise RepoException('Erro ao buscar aluno por apelido - Contatar ADM')

    def get_with_mascote(self, aluno_id: int) -> Optional[Aluno]:
        """Retorna o aluno com a relação `mascote` carregada."""
        try:
            stmt = select(Aluno).options(selectinload(Aluno.mascote)).filter_by(id=aluno_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar mascote do aluno - Contatar ADM')

    def get_with_interesses(self, aluno_id: int) -> Optional[Aluno]:
        """Retorna o aluno com a relação `interesses` carregada."""
        try:
            stmt = select(Aluno).options(selectinload(Aluno.interesses)).filter_by(id=aluno_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar interesses do aluno - Contatar ADM')

    def get_with_disciplinas(self, aluno_id: int) -> Optional[Aluno]:
        """Retorna o aluno com a relação `disciplinas` carregada."""
        try:
            stmt = select(Aluno).options(selectinload(Aluno.disciplinas)).filter_by(id=aluno_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar disciplinas do aluno - Contatar ADM')

    def get_with_desempenhos(self, aluno_id: int) -> Optional[Aluno]:
        """Retorna o aluno com a relação `desempenhos` carregada."""
        try:
            stmt = select(Aluno).options(selectinload(Aluno.desempenhos)).filter_by(id=aluno_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar desempenhos do aluno - Contatar ADM')
