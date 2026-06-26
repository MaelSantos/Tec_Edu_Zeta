from typing import Optional, List
from fastapi import APIRouter, HTTPException, status

from api.schemas.interesse_schema import InteresseCreate, InteresseResponse

router = APIRouter(
    prefix="/api/interesses",
    tags=["Interesses"],
)


# @router.post("/save", response_model=InteresseResponse, status_code=status.HTTP_201_CREATED)
# async def criar_interesse(interesse_data: InteresseCreate) -> InteresseResponse:
#     """Criar um novo Interesse."""
#     try:
#         aluno = aluno_service.save_aluno(aluno_data)
#         if not aluno:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Erro ao criar aluno",
#             )
#         return AlunoResponse.model_validate(aluno)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))