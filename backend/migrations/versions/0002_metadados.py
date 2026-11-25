"""Adiciona metadados opcionais e garante um vínculo Goodreads por livro."""

import sqlalchemy as sa
from alembic import op


revision = "0002_metadados"
down_revision = "0001_catalogo"
branch_labels = None
depends_on = None

INDICE_BOOK_ID = "ix_goodreadsbook_book_id"


def upgrade() -> None:
    conexao = op.get_bind()
    inspetor = sa.inspect(conexao)
    existentes = {coluna["name"] for coluna in inspetor.get_columns("book")}
    colunas = (
        sa.Column("capa_url", sa.String),
        sa.Column("nota", sa.Float),
        sa.Column("avaliacoes", sa.Integer),
        sa.Column("paginas", sa.Integer),
        sa.Column("editora", sa.String),
        sa.Column("url", sa.String),
    )
    for coluna in colunas:
        if coluna.name not in existentes:
            op.add_column("book", coluna)

    for indice in inspetor.get_indexes("goodreadsbook"):
        if indice["name"] == INDICE_BOOK_ID:
            if indice["column_names"] != ["book_id"] or indice.get("dialect_options"):
                raise RuntimeError(f"Índice {INDICE_BOOK_ID} tem uma definição incompatível.")
            if indice["unique"]:
                return
            op.drop_index(INDICE_BOOK_ID, table_name="goodreadsbook")
            break

    duplicado = conexao.exec_driver_sql(
        "SELECT book_id FROM goodreadsbook GROUP BY book_id HAVING COUNT(*) > 1 LIMIT 1"
    ).scalar()
    if duplicado is not None:
        raise RuntimeError(f"O livro {duplicado} tem mais de um vínculo Goodreads.")
    op.create_index(INDICE_BOOK_ID, "goodreadsbook", ["book_id"], unique=True)


def downgrade() -> None:
    raise NotImplementedError("Remover esta revisão pode apagar metadados. Restaure um backup.")
