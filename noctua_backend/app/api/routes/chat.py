from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.banco import obter_sessao
from app.repositories.repositorio_documento import RepositorioDocumento
from app.repositories.repositorio_trecho import RepositorioTrecho
from app.schemas.chat import ConsultaChat, FonteChat, RespostaChat
from app.services.servico_chat import ServicoChat
from app.services.servico_rag import ServicoRag

roteador = APIRouter(prefix="/chat", tags=["chat"])


def obter_servico_chat(sessao: Session = Depends(obter_sessao)) -> ServicoChat:
    """Monta o fluxo de chat com os repositories da requisição."""
    return ServicoChat(
        servico_rag=ServicoRag(RepositorioTrecho(sessao)),
        repositorio_documento=RepositorioDocumento(sessao),
    )


@roteador.post("", response_model=RespostaChat)
async def conversar(
    consulta: ConsultaChat,
    servico: ServicoChat = Depends(obter_servico_chat),
) -> RespostaChat:
    """Responde usando apenas o contexto dos documentos da organização atual."""
    try:
        resultado = servico.responder(consulta.question)
    except RuntimeError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O chat não está disponível. Verifique a configuração da OpenAI.",
        ) from erro

    return RespostaChat(
        answer=resultado.resposta,
        sources=[FonteChat(document=fonte.documento, page=fonte.pagina) for fonte in resultado.fontes],
    )
