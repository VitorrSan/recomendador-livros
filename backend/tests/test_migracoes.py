import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine

from app import db
from app.models import Book, GoodreadsBook


@pytest.fixture
def banco_legado(tmp_path, monkeypatch):
    caminho = tmp_path / "legado.db"
    engine = create_engine(f"sqlite:///{caminho.as_posix()}")
    monkeypatch.setattr(db, "engine", engine)
    with engine.begin() as conexao:
        conexao.exec_driver_sql(
            """
            CREATE TABLE book (
                id INTEGER PRIMARY KEY, titulo VARCHAR NOT NULL, autor VARCHAR NOT NULL,
                ano_publicacao INTEGER, genero VARCHAR, descricao VARCHAR NOT NULL, capa_url VARCHAR
            )
            """
        )
        conexao.exec_driver_sql(
            """
            CREATE TABLE goodreadsbook (
                goodreads_id VARCHAR NOT NULL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES book (id)
            )
            """
        )
        conexao.exec_driver_sql(
            "INSERT INTO book (id, titulo, autor, descricao, capa_url) VALUES (?, ?, ?, ?, ?)",
            (42, "Livro legado", "Equipe", "Sinopse.", "https://example.org/capa.jpg"),
        )
        conexao.exec_driver_sql("INSERT INTO goodreadsbook VALUES ('123', 42)")
    try:
        yield engine
    finally:
        engine.dispose()


def test_migra_banco_legado_e_preserva_ids_ao_reiniciar(banco_legado):
    db.atualizar_banco()
    db.atualizar_banco()

    with banco_legado.connect() as conexao:
        assert conexao.exec_driver_sql("SELECT version_num FROM alembic_version").scalar_one() == (
            "0002_metadados"
        )

    with Session(banco_legado) as session:
        livro = session.get(Book, 42)
        assert session.get(GoodreadsBook, "123").book_id == 42
        assert livro.titulo == "Livro legado"
        assert livro.capa_url == "https://example.org/capa.jpg"
        assert livro.nota is None

        session.add(GoodreadsBook(goodreads_id="456", book_id=42))
        with pytest.raises(IntegrityError):
            session.commit()


def test_migracao_reverte_mudancas_quando_ha_vinculos_duplicados(banco_legado):
    with banco_legado.begin() as conexao:
        conexao.exec_driver_sql("INSERT INTO goodreadsbook VALUES ('456', 42)")

    with pytest.raises(RuntimeError, match="livro 42 tem mais de um vínculo"):
        db.atualizar_banco()

    inspetor = inspect(banco_legado)
    assert not inspetor.has_table("alembic_version")
    assert "nota" not in {coluna["name"] for coluna in inspetor.get_columns("book")}
    with banco_legado.connect() as conexao:
        assert conexao.exec_driver_sql("SELECT COUNT(*) FROM goodreadsbook").scalar_one() == 2
