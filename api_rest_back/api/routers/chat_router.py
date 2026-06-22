from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas.chat_schema import ChatRequest
from api.services.chat_service import generate_chat_stream


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
    stream_generator = generate_chat_stream(request.prompt)

    # Retornamos a resposta em formato de stream
    return StreamingResponse(stream_generator, media_type="text/plain")