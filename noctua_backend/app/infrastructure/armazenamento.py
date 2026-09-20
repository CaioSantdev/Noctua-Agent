from pathlib import Path


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
