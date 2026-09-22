import uuid
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.core.config import obter_configuracoes
from app.infrastructure.armazenamento import ArmazenamentoLocal
from app.infrastructure.fila_tarefas import (
    ErroEnfileiramentoDocumento,
    enfileirar_processamento_documento,
)
from app.models.documento import Documento, StatusDocumento
from app.repositories.repositorio_documento import RepositorioDocumento
from app.repositories.repositorio_trecho import RepositorioTrecho
from app.services.servico_rag import ServicoRag

TAMANHO_MAXIMO_BYTES = 10 * 1024 * 1024
EXTENSOES_PERMITIDAS = {".pdf", ".txt"}


class ErroDocumento(ValueError):
    """Indica que o arquivo não atende às regras de documentos."""


class ErroProcessamentoDocumento(RuntimeError):
    """Indica que um arquivo válido não pôde ser processado."""


class ServicoDocumento:
    """Orquestra armazenamento, extração e persistência de documentos."""

    def __init__(self, repositorio: RepositorioDocumento, organizacao_id: uuid.UUID) -> None:
        self.repositorio = repositorio
        self.organizacao_id = organizacao_id
        self.armazenamento = ArmazenamentoLocal(obter_configuracoes().diretorio_arquivos)
        self.servico_rag = ServicoRag(RepositorioTrecho(repositorio.sessao))

    def criar(self, nome_arquivo: str, conteudo: bytes) -> Documento:
        """Valida, armazena e envia um documento para processamento assíncrono."""
        extensao = self._validar_arquivo(nome_arquivo, conteudo)
        identificador = uuid.uuid4()
        nome_armazenado = f"{identificador}{extensao}"
        caminho = self.armazenamento.salvar(nome_armazenado, conteudo)
        documento = Documento(
            id=identificador,
            organizacao_id=self.organizacao_id,
            nome_arquivo=Path(nome_arquivo).name,
            extensao=extensao,
            tamanho_bytes=len(conteudo),
            caminho_arquivo=caminho,
            status=StatusDocumento.PENDENTE,
        )

        try:
            documento = self.repositorio.adicionar(documento)
        except Exception:
            self.armazenamento.remover(caminho)
            raise

        try:
            enfileirar_processamento_documento(documento.id)
        except ErroEnfileiramentoDocumento:
            documento.status = StatusDocumento.FALHOU
            self.repositorio.atualizar(documento)
            raise
        return documento

    def listar(self) -> list[Documento]:
        """Lista todos os documentos persistidos."""
        return self.repositorio.listar(self.organizacao_id)

    def obter(self, identificador: uuid.UUID) -> Documento | None:
        """Obtém um documento persistido pelo identificador."""
        return self.repositorio.obter_por_id(
            identificador, self.organizacao_id
        )

    def reindexar(self, identificador: uuid.UUID) -> Documento | None:
        """Envia a reindexação de um documento existente para o worker."""
        documento = self.obter(identificador)
        if documento is None:
            return None
        documento.status = StatusDocumento.PENDENTE
        documento = self.repositorio.atualizar(documento)
        try:
            enfileirar_processamento_documento(documento.id)
        except ErroEnfileiramentoDocumento:
            documento.status = StatusDocumento.FALHOU
            self.repositorio.atualizar(documento)
            raise
        return documento

    def processar(self, documento: Documento) -> Documento:
        """Extrai texto, gera embeddings e atualiza o estado do documento."""
        documento.status = StatusDocumento.PROCESSANDO
        self.repositorio.atualizar(documento)

        try:
            conteudo = self.armazenamento.ler(documento.caminho_arquivo)
            documento.texto_extraido = self._extrair_texto(documento.extensao, conteudo)
            self.servico_rag.indexar_documento(documento)
            documento.status = StatusDocumento.PRONTO
            return self.repositorio.atualizar(documento)
        except Exception as erro:
            documento.status = StatusDocumento.FALHOU
            self.repositorio.atualizar(documento)
            raise ErroProcessamentoDocumento(
                "Não foi possível extrair ou indexar o conteúdo do arquivo."
            ) from erro

    def _validar_arquivo(self, nome_arquivo: str, conteudo: bytes) -> str:
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise ErroDocumento("Somente arquivos PDF e TXT são permitidos.")
        if not conteudo:
            raise ErroDocumento("O arquivo enviado está vazio.")
        if len(conteudo) > TAMANHO_MAXIMO_BYTES:
            raise ErroDocumento("O arquivo excede o limite de 10 MB.")
        if extensao == ".pdf" and len(PdfReader(BytesIO(conteudo)).pages) > obter_configuracoes().max_paginas_pdf:
            raise ErroDocumento(
                f"O PDF excede o limite de {obter_configuracoes().max_paginas_pdf} páginas."
            )
        return extensao

    def _extrair_texto(self, extensao: str, conteudo: bytes) -> str:
        if extensao == ".txt":
            return conteudo.decode("utf-8")

        leitor = PdfReader(BytesIO(conteudo))
        return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
