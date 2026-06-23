from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models.exercicio_model import Exercicio
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException
from api.repositories.database import session

class ExercicioRepo(BaseRepo):
    def get_with_questoes(self, exercicio_id: int) -> Optional[Exercicio]:
        try:
            stmt = select(Exercicio).options(selectinload(Exercicio.questoes)).filter_by(id=exercicio_id)
            return session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar exercicio com questoes - Contatar ADM')
