
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.db import get_session
from app.models import Book


def test_listar_livros(tmp_path):

    caminho = tmp_path / "teste.db"

    engine_teste = create_engine(
        f"sqlite:///{caminho.as_posix()}",
        connect_args={"check_same_thread": False}
    )

    SQLModel.metadata.create_all(engine_teste)

    def get_session_teste():
        with Session(engine_teste) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_teste

    try:
        client = TestClient(app)

        # Teste do catálogo vazio
        resposta = client.get("/books")

        assert resposta.status_code == 200
        assert resposta.json() == []

        # Insere um registro somente no banco de teste
        with Session(engine_teste) as session:
            livro = Book(
                titulo="Livro de teste",
                autor="Autor de teste",
                descricao="Descrição para validar a API"
            )
            session.add(livro)
            session.commit()

        # Teste do catálogo com um registro
        resposta = client.get("/books")

        assert resposta.status_code == 200
        assert len(resposta.json()) == 1
        assert resposta.json()[0]["titulo"] == "Livro de teste"

    finally:
        app.dependency_overrides.clear()
        engine_teste.dispose()
