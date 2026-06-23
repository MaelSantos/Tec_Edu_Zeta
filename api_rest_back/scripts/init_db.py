"""
Script para inicializar o banco de dados e criar todas as tabelas.
Deve ser executado uma vez antes de usar a aplicação.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.repositories.database import engine
from api.models.base import Base

# Importa TODOS os models para que sejam registrados no Base.metadata
# Isso é necessário para que create_all() saiba que tabelas criar
from api.models.aluno_model import Aluno
from api.models.mascote_model import Mascote
from api.models.interesse_model import Interesse
from api.models.disciplina_model import Disciplina
from api.models.desempenho_model import Desempenho
from api.models.conteudo_model import Conteudo
from api.models.exercicio_model import Exercicio
from api.models.questao_model import Questao
from api.models.revisao_model import Revisao


def init_db():
    # print("Limpando o banco de dados...")
    # Base.metadata.drop_all(bind=engine)  # Limpa o banco de dados antes de criar as tabelas
    """Cria todas as tabelas no banco de dados."""
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✓ Banco de dados inicializado com sucesso!")


if __name__ == "__main__":
    init_db()
