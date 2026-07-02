import json
from typing import List

from agno.run import RunContext
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.nvidia import Nvidia
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.valyu import ValyuTools
from agno.db import PostgresDb
from dotenv import load_dotenv
from fastapi import HTTPException, status
from api.utils import constants
from api.utils import instructions
from api.schemas.chat_schema import AvaliacaoResponse, QuizResponse, ResumoResponse, RevisaoResponse
from api.schemas.chat_schema import QuizResponse
from api.utils.enums import TipoAcao

load_dotenv()

class ChatService:
    """
    Serviço responsável por interagir com o Agno para gerar respostas de chat.
    """
    def __init__(self):
        self.tutor_agent = self.criar_agente(stream_response=True)
    
    def generate_chat_stream(self, message: str):
        """
        Função geradora que se comunica com o Agno e faz o yield dos pedaços de texto.
        """
        response_stream = self.tutor_agent.run(message, stream=True)
        
        for chunk in response_stream:
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk

    def criar_agente(self, stream_response=True):
        """
        Função para criar e configurar o agente do Agno com as instruções e ferramentas necessárias.
        """
        agente = Agent(
            id=instructions.AGENT_ID,
            name=instructions.AGENT_NAME,
            role=instructions.AGENT_ROLE,
            model=Gemini(id=constants.AI_MODEL_ID),
            # model=Nvidia(id=constants.AI_MODEL_ID),
            tools=[DuckDuckGoTools(), ValyuTools()],
            instructions=instructions.AGENT_INSTRUCTIONS,
            db=PostgresDb(db_url=constants.AGNO_DATABASE_URL),
            add_datetime_to_context=True,
            add_history_to_context=True,
            num_history_runs=3,
            markdown=True,
            use_json_mode=True,
            stream=stream_response,
        )
        return agente
    
    def gerar_resposta_chat(self, message: str, interesses_list: List[str], personalizacao_agente: json, mode = TipoAcao.RESUMO):
        """
        Função para buscar a resposta do chat usando o agente do Agno.
        :param message: Mensagem do usuário.
        :param interesses_list: Lista de interesses do aluno.
        :param personalizacao_agente: Dados de personalização do agente.
        """
        apelido = personalizacao_agente.get("apelido", "Aluno")
        disciplina_aluno = personalizacao_agente.get("disciplina", "")
        topicos = personalizacao_agente.get("topicos", "")
        # nome_mascote = personalizacao_agente.get("nome_mascote", "Zetinho")
        # personalidade_mascote = personalizacao_agente.get("personalidade_mascote", "Alegre e Enthusiasta")
        # tipo_mascote = personalizacao_agente.get("tipo_mascote", "Capivara")
        # linguagem_mascote = personalizacao_agente.get("linguagem_mascote", "Informal e Amigável")
        # estado_mascote = personalizacao_agente.get("estado_mascote", "Feliz")
        nome_mascote = "Nex"
        personalidade_mascote = "Alegre e Enthusiasta"
        tipo_mascote = "Capivara"
        linguagem_mascote = "Informal e Amigável"
        estado_mascote = "Feliz"
        
        contexto_agente = instructions.gerar_contexto_agente(
            interesses_list, apelido, disciplina_aluno, topicos, nome_mascote, personalidade_mascote, tipo_mascote, linguagem_mascote, estado_mascote
        )
        
        if mode == TipoAcao.RESUMO:
            self.tutor_agent.response_model = ResumoResponse
        elif mode == TipoAcao.EXERCICIO:
            self.tutor_agent.response_model = AvaliacaoResponse
        elif mode == TipoAcao.REVISAO:
            self.tutor_agent.response_model = RevisaoResponse
        elif mode == TipoAcao.QUIZ:
            self.tutor_agent.response_model = QuizResponse
            
        # run_context = RunContext(dependencies=personalizacao_agente)

        response_stream = None
        try:
            response_stream = self.tutor_agent.run(f"{contexto_agente}\n\nSolicitação do aluno:{message}", stream=False)
        except Exception as e:
            print(f"Erro ao gerar resposta do Agno: {str(e)}")  # Log do erro para depuração
            error_message = str(e)
            error_lower = error_message.lower()
            if "high demand" in error_lower or "503" in error_lower or "unavailable" in error_lower:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="O serviço de IA está temporariamente indisponível devido à alta demanda. Tente novamente mais tarde."
                )
            if "quota" in error_lower or "credit" in error_lower or "tokens" in error_lower:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Não foi possível gerar a resposta porque os créditos/tokens acabaram. Tente novamente mais tarde."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno no serviço de IA. Por favor, tente novamente mais tarde."
            )

        print(f"Resposta do Agno (raw): {response_stream}")  # Log da resposta bruta do Agno para depuração

        # Se o objeto retornado tem atributo content
        if hasattr(response_stream, "content"):
            content = response_stream.content
        else:
            content = response_stream

        print(f"Resposta do Agno: {content}")  # Log da resposta do Agno para depuração
        return content
