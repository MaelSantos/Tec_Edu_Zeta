from typing import Optional, List
from fastapi import APIRouter, HTTPException, status

from api.schemas.aluno_schema import (
    AlunoCreate,
    AlunoUpdate,
    AlunoResponse,
    AlunoWithDisciplinas,
    AlunoWithInteresses,
    AlunoWithDesempenhos,
    AlunoWithMascote,
)
from api.services.aluno_service import AlunoService
from api.schemas.interesse_schema import InteresseAlunoCreate


router = APIRouter(
    prefix="/api/alunos",
    tags=["Alunos"],
)

aluno_service = AlunoService()


@router.post("/save", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
async def criar_aluno(aluno_data: AlunoCreate) -> AlunoResponse:
    """Criar um novo aluno."""
    try:
        aluno = aluno_service.save_aluno(aluno_data)
        if not aluno:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar aluno",
            )
        return AlunoResponse.model_validate(aluno)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.post("/interesses/save", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
async def criar_interesse(interesse_aluno: InteresseAlunoCreate) -> AlunoResponse:
    """Criar um novo interesse."""
    try:
        aluno = aluno_service.save_interesses(interesse_aluno)
        if not aluno:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar interesse",
            )
        return AlunoResponse.model_validate(aluno)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/username/{username}", response_model=AlunoResponse)
async def obter_aluno_por_username(username: str) -> AlunoResponse:
    """Obter aluno por apelido (username)."""
    aluno = aluno_service.get_aluno_by_username(username)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    
    return AlunoResponse.model_validate(aluno)


@router.get("/{aluno_id}/disciplinas", response_model=AlunoWithDisciplinas)
async def obter_aluno_com_disciplinas(aluno_id: int) -> AlunoWithDisciplinas:
    """Obter aluno com suas disciplinas carregadas (eager-loading)."""
    aluno = aluno_service.get_with_disciplinas(aluno_id)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoWithDisciplinas.model_validate(aluno)


@router.get("/{aluno_id}/interesses", response_model=AlunoWithInteresses)
async def obter_aluno_com_interesses(aluno_id: int) -> AlunoWithInteresses:
    """Obter aluno com seus interesses carregados (eager-loading)."""
    aluno = aluno_service.get_with_interesses(aluno_id)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoWithInteresses.model_validate(aluno)


@router.get("/{aluno_id}/desempenhos", response_model=AlunoWithDesempenhos)
async def obter_aluno_com_desempenhos(aluno_id: int) -> AlunoWithDesempenhos:
    """Obter aluno com seus desempenhos carregados (eager-loading)."""
    aluno = aluno_service.get_with_desempenhos(aluno_id)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoWithDesempenhos.model_validate(aluno)


@router.get("/{aluno_id}/mascote", response_model=AlunoWithMascote)
async def obter_aluno_com_mascote(aluno_id: int) -> AlunoWithMascote:
    """Obter aluno com seu mascote carregado (eager-loading)."""
    aluno = aluno_service.get_with_mascote(aluno_id)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoWithMascote.model_validate(aluno)


@router.get("/{aluno_id}", response_model=AlunoResponse)
async def obter_aluno(aluno_id: int) -> AlunoResponse:
    """Obter aluno por ID."""
    aluno = aluno_service.get_by_id(aluno_id)
    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoResponse.model_validate(aluno)


@router.put("/{aluno_id}", response_model=AlunoResponse)
async def atualizar_aluno(aluno_id: int, aluno_data: AlunoUpdate) -> AlunoResponse:
    """Atualizar aluno por ID."""
    aluno_atualizado = aluno_service.update_aluno(aluno_id, aluno_data)
    if not aluno_atualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado",
        )
    return AlunoResponse.model_validate(aluno_atualizado)

