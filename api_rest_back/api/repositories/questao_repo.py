from typing import Optional, List

from api.models.questao_model import Questao
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException


class QuestaoRepo(BaseRepo):
    def get_by_exercicio(self, exercicio_id: int) -> List[Questao]:
        try:
            return self.session.query(Questao).filter(Questao.exercicio_id == exercicio_id).all()
        except Exception:
            raise RepoException('Erro ao buscar questoes por exercicio - Contatar ADM')
