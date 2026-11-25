import csv

import pytest
from sqlmodel import Session, create_engine, select

from app import db
from app.importar_catalogo import main
from app.models import Book, GoodreadsBook


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = tmp_path / "catalogo.db"
    engine = create_engine(f"sqlite:///{caminho.as_posix()}")
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "DB_PATH", caminho)
    try:
        yield caminho, engine
    finally:
        engine.dispose()


def escrever_csv(tmp_path, linhas):
    caminho = tmp_path / "livros.csv"
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=[
                "title", "author", "description", "url", "year", "genre", "book_cover",
                "avg_rating", "num_ratings", "pages", "publisher",
            ],
        )
        escritor.writeheader()
        escritor.writerows(linhas)
    return str(caminho)


def linha_livro(**campos):
    return {
        "title": "Maré",
        "author": "Ana",
        "description": "Sinopse.",
        "url": "https://www.goodreads.com/book/show/1-mare",
        **campos,
    }


def test_importa_nota_avaliacoes_paginas_editora_e_url(tmp_path, banco):
    _, engine = banco
    caminho = escrever_csv(
        tmp_path,
        [
            linha_livro(
                avg_rating="4.25", num_ratings="12345.0", pages="320.0", publisher=" Editora X "
            ),
            linha_livro(title="Chuva", url="https://goodreads.com/book/show/2-chuva"),
        ],
    )

    main([caminho, "--aplicar"])

    with Session(engine) as sessao:
        mare, chuva = sessao.exec(select(Book).order_by(Book.id)).all()
        assert (mare.nota, mare.avaliacoes, mare.paginas, mare.editora) == (
            4.25, 12345, 320, "Editora X"
        )
        assert mare.url == "https://www.goodreads.com/book/show/1"
        assert (chuva.nota, chuva.avaliacoes, chuva.paginas, chuva.editora) == (
            None, None, None, None
        )
        assert chuva.url == "https://www.goodreads.com/book/show/2"


@pytest.mark.parametrize(
    "coluna, valor",
    [
        ("avg_rating", "9"),
        ("avg_rating", "-0.1"),
        ("avg_rating", "abc"),
        ("avg_rating", "nan"),
        ("avg_rating", "inf"),
        ("avg_rating", "-inf"),
        ("num_ratings", "-1"),
        ("num_ratings", "2.5"),
        ("num_ratings", "12,345"),
        ("num_ratings", "1,,2"),
        ("num_ratings", str(db.SQLITE_MAX_INTEGER + 1)),
        ("pages", "-1"),
        ("pages", "320.5"),
        ("pages", "1,000"),
        ("pages", str(db.SQLITE_MAX_INTEGER + 1)),
    ],
)
def test_rejeita_campo_extra_invalido_antes_de_abrir_banco(
    tmp_path, banco, coluna, valor, capsys
):
    caminho_banco, _ = banco
    caminho = escrever_csv(tmp_path, [linha_livro(**{coluna: valor})])

    with pytest.raises(SystemExit) as erro:
        main([caminho, "--aplicar"])

    assert erro.value.code == 1
    mensagem = capsys.readouterr().err
    assert coluna in mensagem
    assert "Linha 2" in mensagem
    assert not caminho_banco.exists()


def test_aceita_limites_da_nota_e_inteiros_do_sqlite(tmp_path, banco):
    _, engine = banco
    caminho = escrever_csv(
        tmp_path,
        [
            linha_livro(
                avg_rating="0", num_ratings=str(db.SQLITE_MAX_INTEGER),
                pages=str(db.SQLITE_MAX_INTEGER),
            ),
            linha_livro(
                url="https://goodreads.com/book/show/2-chuva", avg_rating="5", num_ratings="0"
            ),
        ],
    )

    main([caminho, "--aplicar"])

    with Session(engine) as sessao:
        primeiro, segundo = sessao.exec(select(Book).order_by(Book.id)).all()
        assert (primeiro.nota, primeiro.avaliacoes, primeiro.paginas) == (
            0, db.SQLITE_MAX_INTEGER, db.SQLITE_MAX_INTEGER
        )
        assert (segundo.nota, segundo.avaliacoes, segundo.paginas) == (5, 0, None)


def test_reimportacao_completa_ausentes_e_preserva_dados_ids_e_url(tmp_path, banco):
    _, engine = banco
    with engine.begin() as conexao:
        conexao.exec_driver_sql("BEGIN IMMEDIATE")
        db.preparar_banco(conexao)
    with Session(engine) as sessao:
        preservado = Book(
            id=7, titulo="Título preservado", autor="Autora preservada",
            descricao="Descrição preservada.", ano_publicacao=1999, genero="Fantasia",
            capa_url="https://covers.example.org/original.jpg", nota=4.8,
            avaliacoes=0, paginas=100, editora="Editora original",
            url="https://www.goodreads.com/book/show/1-original",
        )
        incompleto = Book(id=31, titulo="Chuva", autor="Bruno", descricao="Conto.")
        sessao.add_all([preservado, incompleto])
        sessao.flush()
        sessao.add_all(
            [
                GoodreadsBook(goodreads_id="1", book_id=7),
                GoodreadsBook(goodreads_id="2", book_id=31),
            ]
        )
        sessao.commit()
        sessao.refresh(preservado)
        dados_preservados = preservado.model_dump()

    caminho = escrever_csv(
        tmp_path,
        [
            linha_livro(
                year="2025", genre="Aventura", book_cover="https://covers.example.org/nova.jpg",
                avg_rating="3.1", num_ratings="400", pages="900", publisher="Outra editora",
            ),
            linha_livro(
                title="Chuva alterada", url="https://goodreads.com/book/show/2-chuva",
                avg_rating="4.1", num_ratings="900.0", pages="200.0", publisher="Ed",
                book_cover="https://covers.example.org/chuva.jpg",
            ),
        ],
    )
    main([caminho, "--aplicar"])
    with Session(engine) as sessao:
        assert sessao.get(Book, 7).model_dump() == dados_preservados
        completado = sessao.get(Book, 31)
        assert (completado.titulo, completado.autor, completado.descricao) == (
            "Chuva", "Bruno", "Conto."
        )
        assert (completado.nota, completado.avaliacoes, completado.paginas, completado.editora) == (
            4.1, 900, 200, "Ed"
        )
        assert completado.url == "https://www.goodreads.com/book/show/2"
        assert completado.capa_url == "https://covers.example.org/chuva.jpg"
        dados_completados = completado.model_dump()

    main([caminho, "--aplicar"])
    with Session(engine) as sessao:
        assert len(sessao.exec(select(Book)).all()) == 2
        assert sessao.get(Book, 7).model_dump() == dados_preservados
        assert sessao.get(Book, 31).model_dump() == dados_completados
        assert dict(sessao.exec(select(GoodreadsBook.goodreads_id, GoodreadsBook.book_id)).all()) == {
            "1": 7, "2": 31
        }


def test_urls_equivalentes_sao_deduplicadas_sem_expor_dados_da_url(tmp_path, banco):
    _, engine = banco
    caminho = escrever_csv(
        tmp_path,
        [
            linha_livro(
                url="https://usuario:senha@goodreads.com/book/show/1-mare?token=teste#trecho",
                avg_rating="4.25",
            ),
            linha_livro(
                url="http://www.goodreads.com/book/show/1-outra-grafia?ref=busca",
                avg_rating="4.25",
            ),
        ],
    )

    main([caminho, "--aplicar"])

    with Session(engine) as sessao:
        livros = sessao.exec(select(Book)).all()
        assert len(livros) == 1
        assert livros[0].url == "https://www.goodreads.com/book/show/1"
        vinculos = sessao.exec(select(GoodreadsBook)).all()
        assert len(vinculos) == 1
        assert vinculos[0].goodreads_id == "1"
        assert vinculos[0].book_id == livros[0].id


def test_rejeita_notas_divergentes_para_o_mesmo_goodreads_antes_de_gravar(tmp_path, banco):
    caminho_banco, _ = banco
    caminho = escrever_csv(
        tmp_path, [linha_livro(avg_rating="4.25"), linha_livro(avg_rating="3.5")]
    )

    with pytest.raises(SystemExit) as erro:
        main([caminho, "--aplicar"])

    assert erro.value.code == 1
    assert not caminho_banco.exists()
