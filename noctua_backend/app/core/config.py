import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Configuracoes:
    """Configurações obtidas do ambiente de execução."""

    url_banco: str
    diretorio_arquivos: str


@lru_cache
def obter_configuracoes() -> Configuracoes:
    """Obtém a configuração necessária para conectar ao PostgreSQL."""
    url_banco = os.getenv("DATABASE_URL")
    if not url_banco:
        raise RuntimeError("A variável de ambiente DATABASE_URL não foi configurada.")

    return Configuracoes(
        url_banco=url_banco,
        diretorio_arquivos=os.getenv("DIRETORIO_ARQUIVOS", "/tmp/noctua-arquivos"),
    )
