import csv

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app import main
from app.db import get_session
from app.models import Book, GoodreadsBook


@pytest.fixture
def contexto_api(tmp_path, monkeypatch):
    pasta = tmp_path / "artefatos"
    pasta.mkdir()
    banco = tmp_path / "recomendacoes.db"
    engine = create_engine(
        f"sqlite:///{banco.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    # IDs internos e Goodreads distintos das posições da matriz.
    livros = [
        (21, "3003"),
        (61, "2002"),
        (7, "4004"),
        (54, "5005"),
        (16, "6006"),
        (33, "7007"),
        (98, "8008"),
        (99, "8911"),
        (17, None),
    ]
    with Session(engine) as session:
        session.add_all(
            Book(
                id=book_id,
                titulo=f"Livro {book_id}",
                autor="Autor de teste",
                descricao="Sinopse para testar recomendações.",
                capa_url="https://covers.example.org/61.jpg" if book_id == 61 else None,
            )
            for book_id, _ in livros
        )
        session.flush()
        session.add_all(
            GoodreadsBook(goodreads_id=goodreads_id, book_id=book_id)
            for book_id, goodreads_id in livros
            if goodreads_id is not None
        )
        session.commit()

    def get_session_teste():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(main, "PASTA_ARTEFATOS", pasta)
    monkeypatch.setitem(main.app.dependency_overrides, get_session, get_session_teste)
    client = TestClient(main.app)
    try:
        yield client, pasta
    finally:
        client.close()
        engine.dispose()


def salvar_artefatos(pasta, vetores, linhas):
    np.save(pasta / "embeddings_livros.npy", np.asarray(vetores, dtype=np.float32))
    with (pasta / "livros_metadata.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["book_id", "url"])
        escritor.writerows(
            (posicao, f"https://www.goodreads.com/book/show/{gid}-livro")
            for posicao, gid in linhas
        )


@pytest.fixture
def artefatos_validos(contexto_api):
    client, pasta = contexto_api
    vetores = [
        [0.8, 0.6],
        [0.96, 0.28],  # Melhor candidato, porém ausente do SQLite.
        [1.0, 0.0],  # Livro de origem.
        [0.6, 0.8],
        [0.28, 0.96],
        [0.0, 1.0],
        [-0.6, 0.8],
        [-0.8, 0.6],
    ]
    # O CSV foi reordenado e só book_id identifica a posição na matriz.
    linhas = [
        (6, "7007"),
        (3, "4004"),
        (2, "3003"),
        (0, "2002"),
        (7, "8008"),
        (4, "5005"),
        (1, "9009"),
        (5, "6006"),
    ]
    salvar_artefatos(pasta, vetores, linhas)
    return client


def test_recomenda_por_id_e_mantem_ranking_com_candidato_ausente(artefatos_validos):
    client = artefatos_validos
    resposta = client.get("/books/21/similar", params={"limit": 2})

    assert resposta.status_code == 200
    resultados = resposta.json()
    assert [item["livro"]["id"] for item in resultados] == [61, 7]
    assert [item["similaridade"] for item in resultados] == pytest.approx([0.8, 0.6])
    assert resultados[0]["livro"]["titulo"] == "Livro 61"
    assert resultados[0]["livro"]["capa_url"] == "https://covers.example.org/61.jpg"

    resposta_padrao = client.get("/books/21/similar")
    assert resposta_padrao.status_code == 200
    assert [item["livro"]["id"] for item in resposta_padrao.json()] == [61, 7, 54, 16, 33]


def test_origem_inexistente_e_livro_sem_id_goodreads(contexto_api):
    client, _ = contexto_api

    assert client.get("/books/999/similar").status_code == 404
    sem_goodreads = client.get("/books/17/similar")
    assert sem_goodreads.status_code == 200
    assert sem_goodreads.json() == []


def test_origem_presente_no_sqlite_mas_sem_vetor(artefatos_validos):
    resposta = artefatos_validos.get("/books/99/similar")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_catalogo_continua_funcionando_sem_artefatos(contexto_api):
    client, _ = contexto_api

    assert client.get("/books/21/similar").status_code == 503
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/books").status_code == 200
    assert client.get("/books/21").json()["id"] == 21


@pytest.mark.parametrize(
    "rota",
    ["/books/21/similar?limit=0", "/books/21/similar?limit=21", f"/books/{2**63}/similar"],
)
def test_validacao_dos_parametros(contexto_api, rota):
    client, _ = contexto_api

    assert client.get(rota).status_code == 422


@pytest.mark.parametrize(
    "outro_vetor, outras_linhas",
    [
        pytest.param([np.nan, 1.0], [(1, "2002")], id="vetor-nao-finito"),
        pytest.param([0.0, 1.0], [(0, "2002")], id="posicao-repetida"),
        pytest.param([0.0, 1.0], [(1, "3003")], id="goodreads-repetido"),
        pytest.param([0.0, 1.0], [], id="quantidade-diferente"),
        pytest.param([0.0, 1.0], [("invalido", "2002")], id="posicao-malformada"),
    ],
)
def test_rejeita_artefatos_inconsistentes(contexto_api, outro_vetor, outras_linhas):
    client, pasta = contexto_api
    salvar_artefatos(
        pasta,
        [[1.0, 0.0], outro_vetor],
        [(0, "3003"), *outras_linhas],
    )

    assert client.get("/books/21/similar").status_code == 503
