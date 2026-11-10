
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.db import get_session
from app.models import Book


@pytest.fixture
def engine_teste(tmp_path):
    caminho = tmp_path / "teste.db"

    engine_teste = create_engine(
        f"sqlite:///{caminho.as_posix()}",
        connect_args={"check_same_thread": False}
    )

    SQLModel.metadata.create_all(engine_teste)

    try:
        yield engine_teste
    finally:
        engine_teste.dispose()


@pytest.fixture
def client(engine_teste, monkeypatch):
    def get_session_teste():
        with Session(engine_teste) as session:
            yield session

    monkeypatch.setitem(app.dependency_overrides, get_session, get_session_teste)
    client = TestClient(app)

    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def catalogo(engine_teste):
    # Insere fora de ordem para verificar a ordenação das páginas por ID.
    with Session(engine_teste) as session:
        for livro_id in range(25, 0, -1):
            session.add(
                Book(
                    id=livro_id,
                    titulo=f"Livro {livro_id}",
                    autor="Autor de teste",
                    descricao="Descrição para validar a paginação",
                )
            )
        session.commit()


def test_listar_livros(client, engine_teste):
    # Teste do catálogo vazio
    resposta = client.get("/books")

    assert resposta.status_code == 200
    assert resposta.json() == []

    # Insere um registro somente no banco de teste
    with Session(engine_teste) as session:
        livro = Book(
            titulo="Livro de teste",
            autor="Autor de teste",
            descricao="Descrição para validar a API",
        )
        session.add(livro)
        session.commit()

    # Teste do catálogo com um registro
    resposta = client.get("/books")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["titulo"] == "Livro de teste"


def test_paginacao_padrao(client, catalogo):
    resposta = client.get("/books")

    assert resposta.status_code == 200
    assert [livro["id"] for livro in resposta.json()] == list(range(1, 21))


def test_offset_sem_limit(client, catalogo):
    resposta = client.get("/books", params={"offset": 20})

    assert resposta.status_code == 200
    assert [livro["id"] for livro in resposta.json()] == [21, 22, 23, 24, 25]


def test_limit_sem_offset(client, catalogo):
    resposta = client.get("/books", params={"limit": 3})

    assert resposta.status_code == 200
    assert [livro["id"] for livro in resposta.json()] == [1, 2, 3]


@pytest.mark.parametrize(
    "offset, limit, ids_esperados",
    [
        (0, 1, [1]),
        (0, 3, [1, 2, 3]),
        (3, 3, [4, 5, 6]),
        (24, 3, [25]),
        (25, 3, []),
        (30, 3, []),
        (0, 100, list(range(1, 26))),
    ],
)
def test_paginas_do_catalogo(client, catalogo, offset, limit, ids_esperados):
    resposta = client.get("/books", params={"offset": offset, "limit": limit})

    assert resposta.status_code == 200
    assert [livro["id"] for livro in resposta.json()] == ids_esperados


@pytest.mark.parametrize(
    "parametro, valor",
    [
        ("offset", -1),
        ("offset", "abc"),
        ("offset", "1.5"),
        ("limit", 0),
        ("limit", -1),
        ("limit", 101),
        ("limit", "abc"),
        ("limit", "1.5"),
    ],
)
def test_parametros_de_paginacao_invalidos(client, parametro, valor):
    resposta = client.get("/books", params={parametro: valor})

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["loc"] == ["query", parametro]
