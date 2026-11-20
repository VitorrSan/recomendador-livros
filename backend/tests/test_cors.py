from contextlib import closing

import pytest
from fastapi.testclient import TestClient

from app.main import criar_app


def preflight(client, origem, metodo="GET"):
    return client.options(
        "/books",
        headers={
            "Origin": origem,
            "Access-Control-Request-Method": metodo,
            "Access-Control-Request-Headers": "Content-Type",
        },
    )


@pytest.mark.parametrize("origem", ["http://localhost:5173", "http://127.0.0.1:5173"])
def test_origem_local_pode_consultar_api(monkeypatch, origem):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    with closing(TestClient(criar_app())) as client:
        consulta_previa = preflight(client, origem)
        resposta = client.get("/health", headers={"Origin": origem})

    assert consulta_previa.status_code == 200
    assert consulta_previa.headers["access-control-allow-origin"] == origem
    assert consulta_previa.headers["access-control-allow-methods"] == "GET"
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == origem


def test_origem_externa_nao_e_permitida_por_padrao(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    with closing(TestClient(criar_app())) as client:
        resposta = preflight(client, "https://outro-site.example.org")

    assert resposta.status_code == 400
    assert "access-control-allow-origin" not in resposta.headers


def test_origens_personalizadas_substituem_padrao_e_so_permitem_get(monkeypatch):
    primeira = "https://frontend.example.org"
    segunda = "https://previews.example.org"
    monkeypatch.setenv("CORS_ORIGINS", f" {primeira}, {segunda} ")

    with closing(TestClient(criar_app())) as client:
        for origem in (primeira, segunda):
            resposta = preflight(client, origem)
            assert resposta.status_code == 200
            assert resposta.headers["access-control-allow-origin"] == origem

        origem_padrao = preflight(client, "http://localhost:5173")
        metodo_invalido = preflight(client, primeira, metodo="POST")

    assert origem_padrao.status_code == 400
    assert "access-control-allow-origin" not in origem_padrao.headers
    assert metodo_invalido.status_code == 400
