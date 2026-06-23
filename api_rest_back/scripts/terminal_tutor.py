import time
import sys
from typing import List
from pathlib import Path

from api.repositories.database import engine
from api.models.base import Base
from api.models.aluno_model import Aluno
from api.models.mascote_model import Mascote
from api.models.interesse_model import Interesse
from api.models.disciplina_model import Disciplina
from api.models.desempenho_model import Desempenho
from api.schemas.aluno_schema import AlunoCreate
from api.services.aluno_service import AlunoService
from api.repositories.interesse_repo import InteresseRepo
from api.repositories.aluno_repo import AlunoRepo
from api.repositories.disciplina_repo import DisciplinaRepo
from api.repositories.desempenho_repo import DesempenhoRepo
from api.services.chat_service import ChatService
from api.utils.enums import TipoAcao, TipoDificuldade
from scripts.init_db import init_db


aluno_repo = AlunoRepo()
interesse_repo = InteresseRepo()
disciplina_repo = DisciplinaRepo()
desempenho_repo = DesempenhoRepo()

chat_service = ChatService()

def stream_print(generator):
    print('\n---\n')
    print(generator.content if hasattr(generator, 'content') else generator, end="", flush=True)
    # for chunk in generator:
    #     print(chunk, end="", flush=True)
    print("\n---\n")


def ensure_interests(aluno: Aluno, interest_names: List[str]):
    # create or fetch Interesse entities, attach to aluno
    for name in interest_names:
        name = name.strip()
        if not name:
            continue
        existing = interesse_repo.get_by_nome(name)
        if existing is None:
            novo = Interesse(nome=name)
            interesse_id = interesse_repo.create(novo)
            existing = interesse_repo.get_by_id(Interesse, interesse_id)
        # attach via AlunoRepo (load fresh aluno to avoid stale session)
            a = aluno_repo.get_by_id(Aluno, aluno.id)
            if existing not in a.interesses:
                a.interesses.append(existing)
                aluno_repo.update()


def ensure_disciplina(nome: str) -> Disciplina:
    existente = disciplina_repo.get_by_nome(nome)
    if existente:
        return existente
    novo = Disciplina(nome=nome, dificuldade=TipoDificuldade.MEDIO)
    novo_id = disciplina_repo.create(novo)
    return disciplina_repo.get_by_id(Disciplina, novo_id)


def record_desempenho(aluno: Aluno, disciplina: Disciplina, acertos: int, total: int, tempo: int):
    d = Desempenho(tempo_de_estudo=tempo, acertos=acertos, erros=(total - acertos), aluno_id=aluno.id, disciplina_id=disciplina.id)
    desempenho_repo.create(d)


def personalize_prompt(aluno: Aluno, interests: List[str]) -> str:
    interests_text = ", ".join(interests) if interests else "nenhum interesse específico"
    return f"Você é um tutor virtual para o aluno {aluno.apelido}. Os interesses principais do aluno são: {interests_text}. Seja empático, claro e gere sugestões de estudo, resumos e exercícios curtos."


def main():
    print("=== Tutor Terminal - Tec Edu Zeta ===")
    aluno_service = AlunoService()

    apelido = input("Informe seu apelido: ").strip()
    aluno = aluno_service.get_aluno_by_username(apelido)
    if not aluno:
        print("Aluno não encontrado. Vou criar um novo perfil.")
        novo = AlunoCreate(apelido=apelido)
        aluno = aluno_service.save_aluno(novo)
        print(f"Aluno criado: {aluno.apelido} - (id={aluno.id})")
    else:
        print(f"Bem-vindo de volta, {aluno.apelido} - (id={aluno.id})!")

    # interests
    if aluno.interesses:
        raw = ', '.join(i.nome for i in aluno.interesses)
        print(f"Seus interesses atuais são: {raw}")
        interests = [s.strip() for s in raw.split(",") if s.strip()]
    elif not aluno.interesses:    
        raw = input("Liste seus principais interesses (separe por vírgula): ").strip()
        interests = [s.strip() for s in raw.split(",") if s.strip()]
        if interests:
            ensure_interests(aluno, interests)
            print("Interesses registrados.")

    prompt_base = personalize_prompt(aluno, interests)

    # interactive loop
    while True:
        print('\n---')
        cmd = input("Digite a disciplina que deseja estudar (ou 'sair' para encerrar): ").strip()
        if cmd.lower() in ("sair", "exit", "quit"):
            print("Encerrando sessão. Até a próxima!")
            break

        disciplina_nome = cmd
        topicos = input("Quais assuntos você tem dificuldade? (resuma): ").strip()

        disciplina = ensure_disciplina(disciplina_nome)

        # ask tutor (agent) for suggestions
        # full_prompt = prompt_base + "\n\nAluno quer estudar: " + disciplina_nome + ".\nDificuldades: " + topicos + ".\n" + "Por favor, sugira métodos de estudo e opções: resumo, exercícios, revisão, quiz."
        print("\nTutor está preparando sugestões...\n")
        # stream_print(chat_service.generate_chat_stream(full_prompt))
        
        prompt = "Por favor, sugira métodos de estudo e opções: resumo, exercícios, revisão, quiz."
        
        personalizacao_agente = {
            "apelido": aluno.apelido,
            "disciplina": disciplina_nome,
            "topicos": topicos,
            "nome_mascote": "Zetinho",
            "personalidade_mascote": "Alegre e Enthusiasta",
            "tipo_mascote": "Cachorro",
            "linguagem_mascote": "Informal e Amigável",
            "estado_mascote": "Feliz"
        }
        
        stream_print(chat_service.gerar_resposta_chat(prompt, interests, personalizacao_agente))

        # action menu
        while True:
            print("Ações disponíveis:")
            print("1) Resumo    2) Exercícios    3) Revisão    4) Quiz    5) Novo assunto    6) Sair")
            escolha = input("Escolha uma ação (número): ").strip()
            if escolha == "1":
                p = prompt_base + f"\nGere um resumo objetivo sobre {disciplina_nome} focado em: {topicos}."
                mode = TipoAcao.RESUMO 
                stream_print(chat_service.gerar_resposta_chat(p, interests, personalizacao_agente, mode))
            elif escolha == "2":
                qtd = input("Quantos exercícios deseja gerar? (padrão 3): ").strip() or "3"
                mode = TipoAcao.EXERCICIO
                p = prompt_base + f"\nGere {qtd} exercícios práticos sobre {disciplina_nome} relacionados a: {topicos}. Forneça enunciados curtos." 
                stream_print(chat_service.gerar_resposta_chat(p, interests, personalizacao_agente, mode))
            elif escolha == "3":
                p = prompt_base + f"\nGere uma rotina de revisão (spaced repetition) para {disciplina_nome} e tópicos: {topicos}."
                mode = TipoAcao.REVISAO
                stream_print(chat_service.gerar_resposta_chat(p, interests, personalizacao_agente, mode))
            elif escolha == "4":
                total = int(input("Quantas perguntas no quiz? (padrão 5): ").strip() or "5")
                mode = TipoAcao.QUIZ
                p = prompt_base + f"\nCrie um quiz de {total} perguntas sobre {disciplina_nome} e {topicos}." 
                stream_print(chat_service.gerar_resposta_chat(p, interests, personalizacao_agente, mode))
                # record desempenho
                acertos = int(input(f"Quantas respostas você acertou (0-{total})? ").strip() or "0")
                tempo = int(input("Quanto tempo (minutos) você gastou no quiz? (apenas número): ").strip() or "0")
                record_desempenho(aluno, disciplina, acertos, total, tempo)
                print("Desempenho registrado.")
            elif escolha == "5":
                break  # volta ao prompt de disciplina
            elif escolha == "6":
                print("Encerrando sessão. Até logo!")
                return
            else:
                print("Opção inválida.")


if __name__ == "__main__":
    init_db()
    main()
