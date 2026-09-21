"""Adiciona tenant aos documentos."""

import uuid

from alembic import op
import sqlalchemy as sa

revision = "20260920_02"
down_revision = "20260920_01"
branch_labels = None
depends_on = None

ID_ORGANIZACAO_PADRAO = uuid.UUID("00000000-0000-0000-0000-000000000001")


def upgrade() -> None:
    """Cria a organização local e associa os documentos existentes a ela."""
    op.create_table(
        "organizacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(sa.text("INSERT INTO organizacoes (id, nome) VALUES (:id, 'Organização local')").bindparams(id=ID_ORGANIZACAO_PADRAO))
    op.add_column("documentos", sa.Column("organizacao_id", sa.Uuid(), nullable=True))
    op.execute(sa.text("UPDATE documentos SET organizacao_id = :id").bindparams(id=ID_ORGANIZACAO_PADRAO))
    op.alter_column("documentos", "organizacao_id", nullable=False)
    op.create_foreign_key("fk_documentos_organizacao", "documentos", "organizacoes", ["organizacao_id"], ["id"])


def downgrade() -> None:
    """Remove o tenant temporário dos documentos."""
    op.drop_constraint("fk_documentos_organizacao", "documentos", type_="foreignkey")
    op.drop_column("documentos", "organizacao_id")
    op.drop_table("organizacoes")
