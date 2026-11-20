import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

import numpy as np


BACKEND = Path(__file__).resolve().parents[1]


def executar_python(codigo, **variaveis):
    ambiente = os.environ.copy()
    for nome in ("BOOKS_DB_PATH", "NLP_ARTIFACTS_DIR", "SQL_ECHO"):
        ambiente.pop(nome, None)
    ambiente.update({nome: str(valor) for nome, valor in variaveis.items()})
    processo = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", "-c", dedent(codigo)],
        cwd=BACKEND,
        env=ambiente,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert processo.returncode == 0, processo.stdout + processo.stderr


def test_configuracao_padrao_preserva_caminhos_locais_e_desliga_sql_echo():
    # Importar os módulos não abre nem altera o banco local.
    executar_python(
        """
        from pathlib import Path
        from app import db
        from app.nlp.recomendacoes import PASTA_ARTEFATOS

        assert db.DB_PATH == Path.cwd() / "books.db"
        assert PASTA_ARTEFATOS == Path.cwd() / "app" / "nlp"
        assert db.engine.echo is False
        """
    )


def test_caminho_configurado_cria_pasta_e_preserva_livros_apos_reiniciar(tmp_path):
    banco = tmp_path / "volume" / "catalogo" / "books.db"
    executar_python(
        """
        from fastapi.testclient import TestClient
        from sqlmodel import Session
        from app import db
        from app.main import criar_app
        from app.models import Book

        assert not db.DB_PATH.parent.exists()
        with TestClient(criar_app()) as client:
            with Session(db.engine) as session:
                session.add(Book(titulo="Livro persistido", autor="Equipe", descricao="Sinopse."))
                session.commit()
            assert client.get("/books").json()[0]["titulo"] == "Livro persistido"
        """,
        BOOKS_DB_PATH=banco,
    )
    assert banco.is_file()
    # Um processo novo reproduz o reinício do servidor usando o mesmo volume.
    executar_python(
        """
        from fastapi.testclient import TestClient
        from app.main import criar_app

        with TestClient(criar_app()) as client:
            resposta = client.get("/books/1")
            assert resposta.status_code == 200
            assert resposta.json()["titulo"] == "Livro persistido"
        """,
        BOOKS_DB_PATH=banco,
    )


def test_importador_usa_banco_configurado_sem_criar_pasta_na_validacao(tmp_path):
    banco = tmp_path / "volume" / "books.db"
    catalogo = tmp_path / "catalogo.csv"
    catalogo.write_text(
        "title,author,description,url\n"
        "Livro importado,Equipe,Sinopse.,https://goodreads.com/book/show/123-livro\n",
        encoding="utf-8",
    )
    executar_python(
        """
        from os import environ
        from sqlmodel import Session, select
        from app import db
        from app.importar_catalogo import main
        from app.models import Book

        main([environ["CATALOGO_TESTE"]])
        assert not db.DB_PATH.parent.exists()
        main([environ["CATALOGO_TESTE"], "--aplicar"])
        assert db.DB_PATH.is_file()
        with Session(db.engine) as session:
            livros = session.exec(select(Book)).all()
            assert len(livros) == 1
            assert livros[0].titulo == "Livro importado"
        """,
        BOOKS_DB_PATH=banco,
        CATALOGO_TESTE=catalogo,
    )


def test_artefatos_sao_lidos_da_pasta_configurada(tmp_path):
    pasta = tmp_path / "nlp"
    pasta.mkdir()
    np.save(pasta / "embeddings_livros.npy", np.array([[1.0, 0.0], [0.8, 0.6]]))
    (pasta / "livros_metadata.csv").write_text(
        "book_id,url\n"
        "0,https://goodreads.com/book/show/123-origem\n"
        "1,https://goodreads.com/book/show/456-similar\n",
        encoding="utf-8",
    )
    executar_python(
        """
        from os import environ
        from pathlib import Path
        from app.main import PASTA_ARTEFATOS, carregar_catalogo

        assert PASTA_ARTEFATOS == Path(environ["NLP_ARTIFACTS_DIR"])
        ranking = carregar_catalogo(PASTA_ARTEFATOS).similares("123", {"456"}, 1)
        assert ranking == [("456", 0.8)]
        """,
        NLP_ARTIFACTS_DIR=pasta,
    )


def test_sql_echo_pode_ser_habilitado_explicitamente():
    executar_python(
        """
        from app import db

        assert db.engine.echo is True
        """,
        SQL_ECHO="true",
    )
