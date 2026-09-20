from fastapi import APIRouter, HTTPException, status

from app.schemas.saude import RespostaSaude
from app.services.servico_saude import ServicoSaude

roteador = APIRouter(tags=["saúde"])


@roteador.get("/health", response_model=RespostaSaude)
async def verificar_saude() -> RespostaSaude:
    """Retorna a disponibilidade da API e de sua dependência de banco."""
    if not ServicoSaude().banco_disponivel():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O banco de dados não está disponível.",
        )

    return RespostaSaude(status="ok")
