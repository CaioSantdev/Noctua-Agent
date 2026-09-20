from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.banco import verificar_conexao


class ServicoSaude:
    """Orquestra a verificação de disponibilidade das dependências."""

    def banco_disponivel(self) -> bool:
        """Informa se uma consulta ao banco pode ser executada."""
        try:
            verificar_conexao()
        except (RuntimeError, SQLAlchemyError):
            return False

        return True
