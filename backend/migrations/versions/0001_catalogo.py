"""Cria as tabelas do catálogo ou adota as tabelas legadas."""

import sqlalchemy as sa
from alembic import op


revision = "0001_catalogo"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    tabelas = sa.inspect(op.get_bind())
    if not tabelas.has_table("book"):
        op.create_table(
            "book",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("titulo", sa.String, nullable=False),
            sa.Column("autor", sa.String, nullable=False),
            sa.Column("ano_publicacao", sa.Integer),
            sa.Column("genero", sa.String),
            sa.Column("descricao", sa.String, nullable=False),
        )
    if not tabelas.has_table("goodreadsbook"):
        op.create_table(
            "goodreadsbook",
            sa.Column("goodreads_id", sa.String, primary_key=True),
            sa.Column("book_id", sa.Integer, sa.ForeignKey("book.id"), nullable=False),
        )


def downgrade() -> None:
    raise NotImplementedError("A revisão inicial pode conter dados legados. Restaure um backup.")
