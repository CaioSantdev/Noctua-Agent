from fastapi import HTTPException, status

from app.services.resiliencia_openai import (
    ErroOpenAiConfiguracao,
    ErroOpenAiIndisponivel,
    ErroOpenAiRequisicao,
)


def converter_erro_openai(erro: RuntimeError) -> HTTPException:
    """Converte erros conhecidos da OpenAI em respostas HTTP seguras."""
    if isinstance(erro, ErroOpenAiRequisicao):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro))
    if isinstance(erro, ErroOpenAiConfiguracao):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(erro))
    if isinstance(erro, ErroOpenAiIndisponivel):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(erro))
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="O serviço de IA está indisponível no momento.",
    )
