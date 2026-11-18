import pytest
from sqlmodel import Session, create_engine, select

from app import db
from app.importar_catalogo import main
from app.models import Book, GoodreadsBook


@pytest.fixture
def banco_importacao(tmp_path, monkeypatch):
    caminho = tmp_path / "catalogo.db"
    engine = create_engine(f"sqlite:///{caminho.as_posix()}")
    monkeypatch.setattr(db, "engine", engine)
    try:
        yield caminho, engine
    finally:
        engine.dispose()


@pytest.fixture
def csv_de_livros(tmp_path):
    caminho = tmp_path / "livros_limpos.csv"
    caminho.write_text(
        "title,author,description,url,year,genre,book_cover\n"
        '"Maré, pedra e vento",Ana Reis,"História sobre o mar, a busca e o retorno.",'
        "https://www.goodreads.com/book/show/123-mare,2024.0,Fantasia,\n"
        "Chuva breve,Bruno Luz,Um conto breve.,https://goodreads.com/book/show/456-chuva,,,"
        "https://covers.example.org/chuva.jpg\n",
        encoding="utf-8-sig",
    )
    return caminho


def test_valida_csv_sem_criar_banco(tmp_path, banco_importacao):
    caminho_banco, _ = banco_importacao
    csv_path = tmp_path / "livros_limpos.csv"
    csv_path.write_text(
        "title,author,description,url\n"
        "Chuva breve,Bruno Luz,Um conto breve.,https://goodreads.com/book/show/456-chuva\n",
        encoding="utf-8",
    )

    main([str(csv_path)])

    assert not caminho_banco.exists()


def test_importa_e_completa_capas_sem_alterar_ids_ou_metadados(csv_de_livros, banco_importacao):
    _, engine = banco_importacao
    # Reproduz a tabela legada, anterior à coluna capa_url.
    with engine.begin() as conexao:
        conexao.exec_driver_sql(
            """
            CREATE TABLE book (
                id INTEGER NOT NULL,
                titulo VARCHAR NOT NULL,
                autor VARCHAR NOT NULL,
                ano_publicacao INTEGER,
                genero VARCHAR,
                descricao VARCHAR NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conexao.exec_driver_sql(
            "INSERT INTO book (id, titulo, autor, descricao) VALUES (?, ?, ?, ?)",
            (1, "O Hobbit", "J. R. R. Tolkien", "A viagem de Bilbo."),
        )

    main([str(csv_de_livros), "--aplicar"])

    with Session(engine) as session:
        ids = {
            item.goodreads_id: item.book_id
            for item in session.exec(select(GoodreadsBook))
        }
        assert ids.keys() == {"123", "456"}
        mare = session.get(Book, ids["123"])
        assert mare.titulo == "Maré, pedra e vento"
        assert mare.autor == "Ana Reis"
        assert mare.descricao == "História sobre o mar, a busca e o retorno."
        assert mare.ano_publicacao == 2024
        assert mare.genero == "Fantasia"
        assert mare.capa_url is None
        chuva = session.get(Book, ids["456"])
        assert chuva.ano_publicacao is None
        assert chuva.genero is None
        assert chuva.capa_url == "https://covers.example.org/chuva.jpg"
        mare_original = mare.model_dump()
        chuva_original = chuva.model_dump()

    csv_de_livros.write_text(
        "title,author,description,url,year,genre,book_cover\n"
        "Título alterado,Autor alterado,Descrição alterada.,"
        "https://goodreads.com/book/show/123-outro-titulo?ref=catalogo,2025,Aventura,"
        "https://covers.example.org/mare.jpg\n"
        "Chuva breve,Bruno Luz,Um conto breve.,https://goodreads.com/book/show/456-chuva,,,"
        "https://covers.example.org/chuva-alterada.jpg\n",
        encoding="utf-8-sig",
    )
    main([str(csv_de_livros), "--aplicar"])

    with Session(engine) as session:
        ids_reimportados = {
            item.goodreads_id: item.book_id
            for item in session.exec(select(GoodreadsBook))
        }
        assert ids_reimportados == ids
        assert len(session.exec(select(Book)).all()) == 3
        mare = session.get(Book, ids["123"])
        assert mare.model_dump() == {
            **mare_original,
            "capa_url": "https://covers.example.org/mare.jpg",
        }
        chuva = session.get(Book, ids["456"])
        assert chuva.model_dump() == chuva_original
        hobbit = session.get(Book, 1)
        assert hobbit.titulo == "O Hobbit"
        assert hobbit.autor == "J. R. R. Tolkien"
        assert hobbit.descricao == "A viagem de Bilbo."
        assert hobbit.capa_url is None


def test_csv_invalido_falha_antes_de_abrir_banco(csv_de_livros, banco_importacao, capsys):
    caminho_banco, _ = banco_importacao
    conteudo = csv_de_livros.read_text(encoding="utf-8-sig")
    csv_de_livros.write_text(
        conteudo.replace("456-chuva,,", "456-chuva,2024.5,"),
        encoding="utf-8-sig",
    )

    with pytest.raises(SystemExit) as exc:
        main([str(csv_de_livros), "--aplicar"])

    assert exc.value.code == 1
    captura = capsys.readouterr()
    assert "Linha 3" in captura.err + captura.out
    assert not caminho_banco.exists()
