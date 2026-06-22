"""Initial database schema.

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mascotes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("personalidade", sa.String(length=50), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("estado", sa.String(length=50), nullable=False),
        sa.Column("linguagem", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "disciplinas",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("dificuldade", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "conteudos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.String(length=1024), nullable=True),
        sa.Column("dificuldade", sa.String(length=50), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), sa.ForeignKey("disciplinas.id"), nullable=False),
    )

    op.create_table(
        "exercicios",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("dificuldade", sa.String(length=50), nullable=False),
        sa.Column("exemplo", sa.String(length=1024), nullable=True),
        sa.Column("conteudo_id", sa.Integer(), sa.ForeignKey("conteudos.id"), nullable=False),
    )

    op.create_table(
        "questaos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("enunciado", sa.String(length=2048), nullable=False),
        sa.Column("dica", sa.String(length=1024), nullable=True),
        sa.Column("resposta_correta", sa.String(length=1024), nullable=False),
        sa.Column("resposta_incorreta1", sa.String(length=1024), nullable=True),
        sa.Column("resposta_incorreta2", sa.String(length=1024), nullable=True),
        sa.Column("resposta_incorreta3", sa.String(length=1024), nullable=True),
        sa.Column("resposta_incorreta4", sa.String(length=1024), nullable=True),
        sa.Column("exercicio_id", sa.Integer(), sa.ForeignKey("exercicios.id"), nullable=False),
    )

    op.create_table(
        "revisoes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("periodo", sa.String(length=120), nullable=False),
        sa.Column("conteudo_id", sa.Integer(), sa.ForeignKey("conteudos.id"), nullable=False),
    )

    op.create_table(
        "alunos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=False),
        sa.Column("nome_usuario", sa.String(length=80), nullable=False),
        sa.Column("senha", sa.String(length=255), nullable=False),
        sa.Column("mascote_id", sa.Integer(), sa.ForeignKey("mascotes.id"), nullable=True),
    )

    op.create_table(
        "interesses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("exemplo", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "desempenhos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("tempo_de_estudo", sa.Integer(), nullable=False),
        sa.Column("acertos", sa.Integer(), nullable=False),
        sa.Column("erros", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("alunos.id"), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), sa.ForeignKey("disciplinas.id"), nullable=False),
    )

    op.create_table(
        "aluno_interesse",
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("alunos.id"), primary_key=True),
        sa.Column("interesse_id", sa.Integer(), sa.ForeignKey("interesses.id"), primary_key=True),
    )

    op.create_table(
        "aluno_disciplina",
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("alunos.id"), primary_key=True),
        sa.Column("disciplina_id", sa.Integer(), sa.ForeignKey("disciplinas.id"), primary_key=True),
    )


def downgrade():
    op.drop_table("aluno_disciplina")
    op.drop_table("aluno_interesse")
    op.drop_table("desempenhos")
    op.drop_table("interesses")
    op.drop_table("alunos")
    op.drop_table("revisoes")
    op.drop_table("questaos")
    op.drop_table("exercicios")
    op.drop_table("conteudos")
    op.drop_table("disciplinas")
    op.drop_table("mascotes")
