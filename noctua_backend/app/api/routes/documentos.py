import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.autenticacao import obter_usuario_autenticado
from app.infrastructure.banco import obter_sessao
from app.models.usuario import Usuario
from app.repositories.repositorio_documento import RepositorioDocumento
from app.schemas.documento import DocumentoDetalhe, DocumentoResumo
from app.services.servico_documento import (
    ErroDocumento,
    ErroProcessamentoDocumento,
    ServicoDocumento,
)

roteador = APIRouter(prefix="/documents", tags=["documentos"])


def obter_servico_documento(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_autenticado),
) -> ServicoDocumento:
    """Monta o serviço com o repositório da requisição atual."""
    return ServicoDocumento(RepositorioDocumento(sessao), usuario.organizacao_id)


@roteador.post("", response_model=DocumentoDetalhe, status_code=status.HTTP_201_CREATED)
async def enviar_documento(
    arquivo: UploadFile = File(...),
    servico: ServicoDocumento = Depends(obter_servico_documento),
) -> DocumentoDetalhe:
    """Recebe um PDF ou TXT, extrai o texto e registra seus metadados."""
    try:
        documento = servico.criar(arquivo.filename or "", await arquivo.read())
    except ErroDocumento as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro
    except ErroProcessamentoDocumento as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro)) from erro

    return DocumentoDetalhe.model_validate(documento)


@roteador.get("", response_model=list[DocumentoResumo])
async def listar_documentos(
    servico: ServicoDocumento = Depends(obter_servico_documento),
) -> list[DocumentoResumo]:
    """Lista os documentos armazenados."""
    return [DocumentoResumo.model_validate(documento) for documento in servico.listar()]


@roteador.get("/{identificador}", response_model=DocumentoDetalhe)
async def obter_documento(
    identificador: uuid.UUID,
    servico: ServicoDocumento = Depends(obter_servico_documento),
) -> DocumentoDetalhe:
    """Retorna os metadados de um documento específico."""
    documento = servico.obter(identificador)
    if documento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")

    return DocumentoDetalhe.model_validate(documento)


@roteador.post("/{identificador}/reindex", response_model=DocumentoDetalhe)
async def reindexar_documento(
    identificador: uuid.UUID,
    servico: ServicoDocumento = Depends(obter_servico_documento),
) -> DocumentoDetalhe:
    """Gera chunks e embeddings de um documento existente."""
    try:
        documento = servico.reindexar(identificador)
    except RuntimeError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A indexação não está disponível. Configure OPENAI_API_KEY.",
        ) from erro

    if documento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")
    return DocumentoDetalhe.model_validate(documento)
