from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.core.config import Configuracoes


class ErroArmazenamento(RuntimeError):
    """Indica uma falha ao acessar o armazenamento de arquivos."""


class ArmazenamentoLocal:
    """Armazena os arquivos enviados no sistema de arquivos local."""

    def __init__(self, diretorio_raiz: str) -> None:
        self.diretorio_raiz = Path(diretorio_raiz)

    def salvar(self, nome_arquivo: str, conteudo: bytes) -> str:
        """Salva um arquivo e retorna seu caminho absoluto."""
        self.diretorio_raiz.mkdir(parents=True, exist_ok=True)
        caminho = self.diretorio_raiz / nome_arquivo
        caminho.write_bytes(conteudo)
        return str(caminho)

    def remover(self, caminho: str) -> None:
        """Remove um arquivo salvo quando a persistência falha."""
        Path(caminho).unlink(missing_ok=True)

    def ler(self, caminho: str) -> bytes:
        """Lê um arquivo previamente armazenado."""
        return Path(caminho).read_bytes()


class ArmazenamentoSupabase:
    """Armazena arquivos privados no Supabase Storage pelo backend."""

    def __init__(self, url: str, chave_servico: str, bucket: str) -> None:
        self.url = url.rstrip("/")
        self.chave_servico = chave_servico
        self.bucket = bucket

    def salvar(self, nome_arquivo: str, conteudo: bytes) -> str:
        """Envia um arquivo ao bucket e retorna a chave persistida."""
        self._requisitar(
            "POST",
            nome_arquivo,
            conteudo,
            {"Content-Type": "application/octet-stream", "x-upsert": "true"},
        )
        return nome_arquivo

    def remover(self, caminho: str) -> None:
        """Remove um objeto do bucket quando a persistência do banco falha."""
        try:
            self._requisitar("DELETE", caminho)
        except ErroArmazenamento:
            # A limpeza não deve ocultar o erro original de persistência.
            return

    def ler(self, caminho: str) -> bytes:
        """Obtém os bytes do objeto para processamento pelo worker."""
        return self._requisitar("GET", caminho)

    def _requisitar(
        self,
        metodo: str,
        caminho: str,
        conteudo: bytes | None = None,
        cabecalhos_extras: dict[str, str] | None = None,
    ) -> bytes:
        cabecalhos = {
            "apikey": self.chave_servico,
            "Authorization": f"Bearer {self.chave_servico}",
        }
        if cabecalhos_extras:
            cabecalhos.update(cabecalhos_extras)
        url = f"{self.url}/storage/v1/object/{quote(self.bucket, safe='')}/{quote(caminho, safe='/')}"
        requisicao = Request(url, data=conteudo, headers=cabecalhos, method=metodo)
        try:
            with urlopen(requisicao, timeout=30) as resposta:
                return resposta.read()
        except (HTTPError, URLError) as erro:
            raise ErroArmazenamento("Não foi possível acessar o armazenamento de documentos.") from erro


def obter_armazenamento(configuracoes: Configuracoes) -> ArmazenamentoLocal | ArmazenamentoSupabase:
    """Seleciona armazenamento local no desenvolvimento ou Supabase na produção."""
    if configuracoes.url_supabase and configuracoes.chave_servico_supabase:
        return ArmazenamentoSupabase(
            configuracoes.url_supabase,
            configuracoes.chave_servico_supabase,
            configuracoes.bucket_documentos_supabase,
        )
    return ArmazenamentoLocal(configuracoes.diretorio_arquivos)
