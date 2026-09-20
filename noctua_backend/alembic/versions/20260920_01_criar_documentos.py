"""Cria a tabela de documentos."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260920_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a estrutura inicial para documentos."""
    status_documento = postgresql.ENUM(
        "pending", "processing", "ready", "failed", name="status_documento", create_type=False
    )
    status_documento.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "documentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome_arquivo", sa.String(length=255), nullable=False),
        sa.Column("extensao", sa.String(length=10), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column("caminho_arquivo", sa.String(length=500), nullable=False),
        sa.Column("texto_extraido", sa.Text(), nullable=True),
        sa.Column("status", status_documento, nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("caminho_arquivo"),
    )


def downgrade() -> None:
    """Remove a estrutura inicial de documentos."""
    op.drop_table("documentos")
    sa.Enum(name="status_documento").drop(op.get_bind(), checkfirst=True)
