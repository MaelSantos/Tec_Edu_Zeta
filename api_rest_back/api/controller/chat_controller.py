from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.valyu import ValyuTools
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from api.util import constants
from api.util import instructions

load_dotenv()

def criar_agente_info(stream_response=True):
    agente = Agent(
        id=instructions.AGENT_ID,
        name=instructions.AGENT_NAME,
        role=instructions.AGENT_ROLE,
        model=Gemini(id=constants.AI_MODEL_ID),
        tools=[DuckDuckGoTools(), ValyuTools()],
        instructions=instructions.AGENT_INSTRUCTIONS,
        db=SqliteDb(db_file=constants.DATABASE_FILE_PATH),
        add_datetime_to_context=True,
        add_history_to_context=True,
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
