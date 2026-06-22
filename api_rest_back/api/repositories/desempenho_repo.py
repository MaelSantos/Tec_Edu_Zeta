from typing import List, Optional

from api.models.desempenho_model import Desempenho
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException


class DesempenhoRepo(BaseRepo):
    def get_by_aluno(self, aluno_id: int) -> List[Desempenho]:
        try:
            return self.session.query(Desempenho).filter(Desempenho.aluno_id == aluno_id).all()
        except Exception:
            raise RepoException('Erro ao buscar desempenhos por aluno - Contatar ADM')

    def get_by_disciplina(self, disciplina_id: int) -> List[Desempenho]:
        try:
            return self.session.query(Desempenho).filter(Desempenho.disciplina_id == disciplina_id).all()
        except Exception:
            raise RepoException('Erro ao buscar desempenhos por disciplina - Contatar ADM')
