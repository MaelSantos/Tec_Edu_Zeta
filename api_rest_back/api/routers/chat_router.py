from fastapi import APIRouter

from api.schemas.chat_schema import ChatRequestPersonalizado
from api.services.chat_service import chat_service

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat IA"],
)

@router.post("/play")
async def chat_personalizado_endpoint(request: ChatRequestPersonalizado):
    resultado = chat_service.gerar_resposta_chat(
        message=request.message,
        interesses_list=request.interesses_list,
        apelido=request.apelido,
        disciplina=request.disciplina,
        topicos=request.topicos,
        nome_mascote=request.nome_mascote,
        personalidade_mascote=request.personalidade_mascote,
        tipo_mascote=request.tipo_mascote,
        linguagem_mascote=request.linguagem_mascote,
        estado_mascote=request.estado_mascote,
        mode=request.mode,
    )
    return resultado