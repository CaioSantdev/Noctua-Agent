"""Cria usuários autenticáveis vinculados a organizações."""

from alembic import op
import sqlalchemy as sa

revision = "20260920_04"
down_revision = "20260920_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabela de usuários e índice único de e-mail."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organizacao_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organizacao_id"], ["organizacoes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)


def downgrade() -> None:
    """Remove usuários e seu índice."""
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
