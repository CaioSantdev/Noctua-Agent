from alembic import context

from app.core.config import obter_configuracoes
from app.models.base import Base
import app.models.documento  # noqa: F401

config = context.config

# O ConfigParser usado pelo Alembic reserva "%" para interpolação. URLs podem
# conter sequências codificadas, como "%24" para uma senha com cifrão.
url_banco_alembic = obter_configuracoes().url_banco.replace("%", "%%")
config.set_main_option("sqlalchemy.url", url_banco_alembic)
metadados_alvo = Base.metadata


def executar_migrations_offline() -> None:
    """Executa migrations sem conexão direta."""
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=metadados_alvo)
    with context.begin_transaction():
        context.run_migrations()


def executar_migrations_online() -> None:
    """Executa migrations com conexão direta."""
    conectavel = context.config.attributes.get("connection")
    if conectavel is None:
        from sqlalchemy import engine_from_config, pool

        conectavel = engine_from_config(
            config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
        )

    with conectavel.connect() as conexao:
        context.configure(connection=conexao, target_metadata=metadados_alvo)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    executar_migrations_offline()
else:
    executar_migrations_online()
