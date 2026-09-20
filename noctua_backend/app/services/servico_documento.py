import uuid
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.core.config import obter_configuracoes
from app.infrastructure.armazenamento import ArmazenamentoLocal
from app.models.documento import Documento, StatusDocumento
from app.repositories.repositorio_documento import RepositorioDocumento

TAMANHO_MAXIMO_BYTES = 10 * 1024 * 1024
EXTENSOES_PERMITIDAS = {".pdf", ".txt"}


class ErroDocumento(ValueError):
    """Indica que o arquivo não atende às regras de documentos."""


class ErroProcessamentoDocumento(RuntimeError):
    """Indica que um arquivo válido não pôde ser processado."""


class ServicoDocumento:
    """Orquestra armazenamento, extração e persistência de documentos."""

    def __init__(self, repositorio: RepositorioDocumento) -> None:
        self.repositorio = repositorio
        self.armazenamento = ArmazenamentoLocal(obter_configuracoes().diretorio_arquivos)

    def criar(self, nome_arquivo: str, conteudo: bytes) -> Documento:
        """Valida, armazena, extrai e persiste um documento síncrono."""
        extensao = self._validar_arquivo(nome_arquivo, conteudo)
        identificador = uuid.uuid4()
        nome_armazenado = f"{identificador}{extensao}"
        caminho = self.armazenamento.salvar(nome_armazenado, conteudo)
        documento = Documento(
            id=identificador,
            nome_arquivo=Path(nome_arquivo).name,
            extensao=extensao,
            tamanho_bytes=len(conteudo),
            caminho_arquivo=caminho,
            status=StatusDocumento.PROCESSANDO,
        )

        try:
            documento = self.repositorio.adicionar(documento)
        except Exception:
            self.armazenamento.remover(caminho)
            raise

        try:
            documento.texto_extraido = self._extrair_texto(extensao, conteudo)
            documento.status = StatusDocumento.PRONTO
            return self.repositorio.atualizar(documento)
        except Exception as erro:
            documento.status = StatusDocumento.FALHOU
            self.repositorio.atualizar(documento)
            raise ErroProcessamentoDocumento("Não foi possível extrair o conteúdo do arquivo.") from erro

    def listar(self) -> list[Documento]:
        """Lista todos os documentos persistidos."""
        return self.repositorio.listar()

    def obter(self, identificador: uuid.UUID) -> Documento | None:
        """Obtém um documento persistido pelo identificador."""
        return self.repositorio.obter_por_id(identificador)

    def _validar_arquivo(self, nome_arquivo: str, conteudo: bytes) -> str:
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise ErroDocumento("Somente arquivos PDF e TXT são permitidos.")
        if not conteudo:
            raise ErroDocumento("O arquivo enviado está vazio.")
        if len(conteudo) > TAMANHO_MAXIMO_BYTES:
            raise ErroDocumento("O arquivo excede o limite de 10 MB.")
        return extensao

    def _extrair_texto(self, extensao: str, conteudo: bytes) -> str:
        if extensao == ".txt":
            return conteudo.decode("utf-8")

        leitor = PdfReader(BytesIO(conteudo))
        return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
