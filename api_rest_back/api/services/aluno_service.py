from typing import Optional

from api.models.aluno_model import Aluno
from api.repositories.aluno_repo import AlunoRepo
from api.schemas.aluno_schema import AlunoCreate, AlunoUpdate


class AlunoService:
    """Serviço para operações de negócio relacionadas à entidade Aluno.

    Esta camada recebe e retorna apenas objetos/Tipos usados pelos routers (schemas ou modelos de domínio),
    criando/atualizando as entidades quando necessário. Routers não instanciam models diretamente.
    """

    def save_aluno(self, aluno_data: AlunoCreate) -> Aluno:
        """Cria um novo Aluno a partir do schema `AlunoCreate` e retorna a entidade criada."""
        with AlunoRepo() as repo:
            novo = Aluno(apelido=aluno_data.apelido, mascote_id=aluno_data.mascote_id)
            aluno_id = repo.create(novo)
            return repo.get_by_id(Aluno, aluno_id)

    def update_aluno(self, aluno_id: int, aluno_update: AlunoUpdate) -> Optional[Aluno]:
        """Atualiza campos do Aluno e retorna a entidade atualizada."""
        with AlunoRepo() as repo:
            aluno = repo.get_by_id(Aluno, aluno_id)
            if not aluno:
                return None
            if aluno_update.apelido is not None:
                aluno.apelido = aluno_update.apelido
            if aluno_update.mascote_id is not None:
                aluno.mascote_id = aluno_update.mascote_id
            repo.update()
            return repo.get_by_id(Aluno, aluno_id)

    def get_by_id(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno por ID."""
        with AlunoRepo() as repo:
            return repo.get_by_id(Aluno, aluno_id)

    def get_aluno_by_username(self, username: str) -> Optional[Aluno]:
        """Busca aluno por apelido (username)."""
        with AlunoRepo() as repo:
            return repo.get_by_username(username)

    def get_with_disciplinas(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com disciplinas carregadas (eager-loading)."""
        with AlunoRepo() as repo:
            return repo.get_with_disciplinas(aluno_id)

    def get_with_interesses(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com interesses carregados (eager-loading)."""
        with AlunoRepo() as repo:
            return repo.get_with_interesses(aluno_id)

    def get_with_desempenhos(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com desempenhos carregados (eager-loading)."""
        with AlunoRepo() as repo:
            return repo.get_with_desempenhos(aluno_id)

    def get_with_mascote(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com mascote carregado (eager-loading)."""
        with AlunoRepo() as repo:
            return repo.get_with_mascote(aluno_id)
