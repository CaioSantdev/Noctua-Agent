from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.autenticacao import obter_usuario_autenticado
from app.api.erros import converter_erro_openai
from app.infrastructure.banco import obter_sessao
from app.models.usuario import Usuario
from app.repositories.repositorio_trecho import RepositorioTrecho
from app.schemas.busca import ConsultaBusca, TrechoRecuperado
from app.services.servico_rag import ServicoRag

roteador = APIRouter(prefix="/search", tags=["busca"])


@roteador.post("", response_model=list[TrechoRecuperado])
async def buscar_conhecimento(
    consulta: ConsultaBusca,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_autenticado),
) -> list[TrechoRecuperado]:
    """Recupera chunks relevantes sem gerar uma resposta por LLM."""
    try:
        resultados = ServicoRag(RepositorioTrecho(sessao)).buscar(
            consulta.pergunta, usuario.organizacao_id
        )
    except RuntimeError as erro:
        raise converter_erro_openai(erro) from erro
    return [
        TrechoRecuperado(
            documento_id=resultado.trecho.documento_id,
            conteudo=resultado.trecho.conteudo,
            pagina=resultado.trecho.pagina,
            similaridade=resultado.similaridade,
        )
        for resultado in resultados
    ]
