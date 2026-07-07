from typing import Optional

from api.models.aluno_model import Aluno
from api.repositories.aluno_repo import AlunoRepo
from api.schemas.aluno_schema import AlunoCreate, AlunoUpdate
from api.models.interesse_model import Interesse
from api.repositories.interesse_repo import InteresseRepo
from api.schemas.interesse_schema import InteresseAlunoCreate


class AlunoService:
    """Serviço para operações de negócio relacionadas à entidade Aluno.

    Esta camada recebe e retorna apenas objetos/Tipos usados pelos routers (schemas ou modelos de domínio),
    criando/atualizando as entidades quando necessário. Routers não instanciam models diretamente.
    """
    def __init__(self):
        self.aluno_repo = AlunoRepo()
        self.interesse_repo = InteresseRepo()

    def save_aluno(self, aluno_data: AlunoCreate) -> Aluno:
        """Cria um novo Aluno a partir do schema `AlunoCreate` e retorna a entidade criada."""
        novo = Aluno(apelido=aluno_data.apelido, mascote_id=aluno_data.mascote_id, ano_escolar=aluno_data.ano_escolar)
        aluno_id = self.aluno_repo.create(novo)
        return self.aluno_repo.get_by_id(Aluno, aluno_id)

    def update_aluno(self, aluno_id: int, aluno_update: AlunoUpdate) -> Optional[Aluno]:
        """Atualiza campos do Aluno e retorna a entidade atualizada."""
        aluno = self.aluno_repo.get_by_id(Aluno, aluno_id)
        if not aluno:
            return None
        if aluno_update.apelido is not None:
            aluno.apelido = aluno_update.apelido
        if aluno_update.mascote_id is not None:
            aluno.mascote_id = aluno_update.mascote_id
        if aluno_update.ano_escolar is not None:
            aluno.ano_escolar = aluno_update.ano_escolar
        self.aluno_repo.update()
        return self.aluno_repo.get_by_id(Aluno, aluno_id)
    
    def save_interesses(self, interesse_aluno: InteresseAlunoCreate) -> Optional[Aluno]:
        """Adiciona interesses ao Aluno e retorna a entidade atualizada."""
        aluno = self.aluno_repo.get_by_id(Aluno, interesse_aluno.aluno_id)
        if not aluno:
            return None
        
        for name in interesse_aluno.interesses:
            name = name.strip()
            if not name:
                continue
            existing = self.interesse_repo.get_by_nome(name)
            if existing is None:
                novo = Interesse(nome=name)
                interesse_id = self.interesse_repo.create(novo)
                existing = self.interesse_repo.get_by_id(Interesse, interesse_id)
            # attach via AlunoRepo (load fresh aluno to avoid stale session)
                if existing not in aluno.interesses:
                    aluno.interesses.append(existing)
                    self.aluno_repo.update()
                
        return self.aluno_repo.get_by_id(Aluno, interesse_aluno.aluno_id)

    def get_by_id(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno por ID."""
        return self.aluno_repo.get_by_id(Aluno, aluno_id)

    def get_aluno_by_username(self, username: str) -> Optional[Aluno]:
        """Busca aluno por apelido (username)."""
        return self.aluno_repo.get_by_username(username)

    def get_with_disciplinas(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com disciplinas carregadas (eager-loading)."""
        return self.aluno_repo.get_with_disciplinas(aluno_id)

    def get_with_interesses(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com interesses carregados (eager-loading)."""
        return self.aluno_repo.get_with_interesses(aluno_id)

    def get_with_desempenhos(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com desempenhos carregados (eager-loading)."""
        return self.aluno_repo.get_with_desempenhos(aluno_id)

    def get_with_mascote(self, aluno_id: int) -> Optional[Aluno]:
        """Busca aluno com mascote carregado (eager-loading)."""
        return self.aluno_repo.get_with_mascote(aluno_id)
