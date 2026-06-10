from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.valyu import ValyuTools
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

load_dotenv()

def criar_agente_info(stream_response=True):
    agente = Agent(
        id="Estude",
        name="Organizador de Disciplinas",
        role="Assistente para ajudar na organização, estruturação e retenção de conteúdos de uma determinada disciplina",
        model=Gemini(id="gemini-3-flash-preview"),
        tools=[DuckDuckGoTools(), ValyuTools()],
        instructions=(
            "Organizar e estruturar conteúdos de uma determinada disciplina, gerando resumos, exercícios e revisões."   
            "Forneça respostas detalhadas, claras e baseadas em fontes confiáveis."
            "Estruture os conteúdos por ordem de dificuldade levando em consideração quais são pré-requisitos para outros."
            "Use a ferramenta DuckDuckGo para obter dados atualizados."
            "Use a ferramenta Valyu para obter trabalhos acadêmicos confiáveis."
        ),
        db=SqliteDb(db_file="./database/estude.db"),
        add_datetime_to_context=True,
        add_history_to_context=True, #mantém o histórico da conversa
        num_history_runs=3,
        markdown=True,
        stream=stream_response,
    )
    return agente

tutor_agent = criar_agente_info(stream_response=True)

def generate_chat_stream(message: str):
    """
    Função geradora que se comunica com o Agno e faz o yield dos pedaços de texto.
    """
    response_stream = tutor_agent.run(message, stream=True)
    
    for chunk in response_stream:
        if hasattr(chunk, 'content') and chunk.content:
            yield chunk.content
        elif isinstance(chunk, str):
            yield chunk

