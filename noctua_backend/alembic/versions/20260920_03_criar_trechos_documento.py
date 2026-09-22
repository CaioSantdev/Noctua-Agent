"""Cria trechos vetoriais dos documentos."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "20260920_03"
down_revision = "20260920_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a tabela com embedding compatível com pgvector."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "trechos_documento",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("documento_id", sa.Uuid(), nullable=False),
        sa.Column("organizacao_id", sa.Uuid(), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("pagina", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["documento_id"], ["documentos.id"]),
        sa.ForeignKeyConstraint(["organizacao_id"], ["organizacoes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove os trechos vetoriais."""
    op.drop_table("trechos_documento")
