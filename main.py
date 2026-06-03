from agno.agent import Agent
# from agno.models.openai import OpenAIChat
# from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.valyu import ValyuTools
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

def criar_agente_info(stream_response=True):
    agente = Agent(
        id="Estude",
        name="Organizador de Disciplinas",
        role="Assistente para ajudar na organização, estruturação e retenção de conteúdos de uma determinada disciplina",
        # model=OpenAIChat(id="gpt-4o-mini"),
        # model=Claude(id="claude-sonnet-4-5"),
        # model=Claude(id="claude-3-haiku"),
        # model=Gemini(id="gemini-2.5-pro-exp"),
        # model=Gemini(id="gemini-2.5-flash"),
        model=Gemini(id="gemini-3-flash-preview"),
        tools=[DuckDuckGoTools(), ValyuTools()],
        instructions=(
            "Organizar e estruturar conteúdos de uma determinada disciplina, gerando resumos, exercícios e revisões."   
            "Forneça respostas detalhadas, claras e baseadas em fontes confiáveis."
            "Estruture os conteúdos por ordem de dificuldade levando em consideração quais são pré-requisitos para outros."
            "Use a ferramenta DuckDuckGo para obter dados atualizados."
            "Use a ferramenta Valyu para obter trabalhos acadêmicos confiáveis."
        ),
        db=SqliteDb(db_file="database/estude.db"),
        add_datetime_to_context=True,
        add_history_to_context=True, #mantém o histórico da conversa
        num_history_runs=3,
        markdown=True,
        stream=stream_response,
    )
    return agente

# Passo 3: interagindo com o agente
def interagir_com_agente(agente):
    print("Informe alguma disciplina que deseja estudar ao agente (digite 'sair' para encerrar):")
    while True:
        try:
            pergunta = input("\nVocê: ").strip()
            if pergunta.lower() in {"sair", "exit", "quit"}:
                print("Encerrando a interação. Até mais!")
                break
            agente.print_response(pergunta, stream=True)
        except KeyboardInterrupt:
            print("\nInteração interrompida.")
            break
        except Exception as e:
            print(f"Erro: {e}")
            break
# if __name__ == "__main__":
meu_agente = criar_agente_info(stream_response=True)
# interagir_com_agente(meu_agente)

# fast_app = FastAPI(title="Teste")
agente_os = AgentOS(agents=[meu_agente])
app = agente_os.get_app()