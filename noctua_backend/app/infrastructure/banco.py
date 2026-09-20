from functools import lru_cache

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import obter_configuracoes


@lru_cache
def obter_engine() -> Engine:
    """Cria o engine SQLAlchemy compartilhado pela aplicação."""
    return create_engine(obter_configuracoes().url_banco, pool_pre_ping=True)


@lru_cache
def obter_fabrica_sessoes() -> sessionmaker[Session]:
    """Cria a fábrica de sessões usada pelos repositories."""
    return sessionmaker(bind=obter_engine(), expire_on_commit=False)


def obter_sessao() -> Generator[Session, None, None]:
    """Fornece uma sessão SQLAlchemy para o ciclo de uma requisição."""
    with obter_fabrica_sessoes()() as sessao:
        yield sessao


def verificar_conexao() -> None:
    """Executa uma consulta mínima para confirmar a conexão com o banco."""
    with obter_engine().connect() as conexao:
        conexao.execute(text("SELECT 1"))
