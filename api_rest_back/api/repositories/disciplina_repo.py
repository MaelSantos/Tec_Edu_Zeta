from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models.disciplina_model import Disciplina
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException
from api.repositories.database import session

class DisciplinaRepo(BaseRepo):
    def get_by_nome(self, nome: str) -> Optional[Disciplina]:
        try:
            return session.query(Disciplina).filter(Disciplina.nome == nome).first()
        except Exception:
            raise RepoException('Erro ao buscar disciplina por nome - Contatar ADM')

    def get_with_conteudos(self, disciplina_id: int) -> Optional[Disciplina]:
        try:
            stmt = select(Disciplina).options(selectinload(Disciplina.conteudos)).filter_by(id=disciplina_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar disciplina com conteudos - Contatar ADM')

    def get_with_desempenhos(self, disciplina_id: int) -> Optional[Disciplina]:
        try:
            stmt = select(Disciplina).options(selectinload(Disciplina.desempenhos)).filter_by(id=disciplina_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar disciplina com desempenhos - Contatar ADM')
