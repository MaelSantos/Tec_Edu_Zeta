from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas.chat_schema import ChatRequest, ChatRequestPersonalizado
from api.services.chat_service import ChatService

chat_service = ChatService()

# Criamos um "mini-aplicativo" de rotas focado apenas no chat
router = APIRouter(
    prefix="/api/chat",
    tags=["Chat IA"],
)

@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Endpoint que recebe a mensagem do usuário e retorna o stream da IA.
    """
    # Passamos a mensagem do modelo Pydantic para a função do controller
    stream_generator = chat_service.generate_chat_stream(request.prompt)

    # Retornamos a resposta em formato de stream
    return StreamingResponse(stream_generator, media_type="text/plain")

@router.post("/play")
async def chat_personalizado_endpoint(request: ChatRequestPersonalizado):
    """
    Endpoint que recebe a mensagem do usuário e retorna um json da IA.
    """
    resultado = chat_service.gerar_resposta_chat(
        message=request.message,
        interesses_list=request.interesses_list,
        personalizacao_agente={
            "apelido": request.apelido,
            "disciplina": request.disciplina,
        },
        mode=request.mode,
    )
    return resultado
    # Passamos a mensagem do modelo Pydantic para a função do controller
    # stream_generator = chat_service.gerar_resposta_chat()

    # # Retornamos a resposta em formato de stream
    # return StreamingResponse(stream_generator, media_type="text/plain")