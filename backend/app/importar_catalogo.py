import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urlsplit

from sqlmodel import Session, select

from app import db
from app.models import Book, GoodreadsBook


CAMPOS_OBRIGATORIOS = {"title", "author", "description", "url"}


def id_goodreads(url: str) -> str:
    endereco = urlsplit(url)
    caminho = re.fullmatch(r"/book/show/([1-9][0-9]*)(?:[-.][^/]+)?/?", endereco.path)
    if (
        endereco.scheme not in {"http", "https"}
        or endereco.hostname not in {"goodreads.com", "www.goodreads.com"}
        or caminho is None
    ):
        raise ValueError("a coluna 'url' deve identificar um livro no Goodreads")
    return caminho.group(1)


def ler_ano(valor: str) -> int | None:
    valor = valor.strip()
    if not valor:
        return None

    formato = re.fullmatch(r"([0-9]{1,4})(?:\.0+)?", valor)
    if formato is None or int(formato.group(1)) == 0:
        raise ValueError("'year' deve ser um ano inteiro de 1 a 9999 ou estar vazio")
    return int(formato.group(1))


def ler_capa(valor: str) -> str | None:
    valor = valor.strip()
    if not valor:
        return None

    endereco = urlsplit(valor)
    if endereco.scheme not in {"http", "https"} or not endereco.hostname:
        raise ValueError("'book_cover' deve ser uma URL HTTP ou HTTPS ou estar vazio")
    return valor


def ler_catalogo(caminho: Path) -> dict[str, Book]:
    livros: dict[str, Book] = {}
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        colunas = leitor.fieldnames or []
        faltantes = CAMPOS_OBRIGATORIOS.difference(colunas)
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}")
        if len(colunas) != len(set(colunas)):
            raise ValueError("O cabeçalho contém colunas duplicadas.")

        for linha in leitor:
            try:
                if None in linha or any(valor is None for valor in linha.values()):
                    raise ValueError("quantidade de campos diferente do cabeçalho")

                campos = {nome: linha[nome].strip() for nome in CAMPOS_OBRIGATORIOS}
                vazios = sorted(nome for nome, valor in campos.items() if not valor)
                if vazios:
                    raise ValueError(f"campos obrigatórios vazios: {', '.join(vazios)}")

                identificador = id_goodreads(campos["url"])
                livro = Book(
                    titulo=campos["title"],
                    autor=campos["author"],
                    descricao=campos["description"],
                    ano_publicacao=ler_ano(linha.get("year", "")),
                    genero=linha.get("genre", "").strip() or None,
                    capa_url=ler_capa(linha.get("book_cover", "")),
                )
                anterior = livros.get(identificador)
                if anterior is not None and anterior.model_dump() != livro.model_dump():
                    raise ValueError(f"o ID Goodreads {identificador} tem cadastros divergentes")
                livros[identificador] = livro
            except ValueError as erro:
                raise ValueError(f"Linha {leitor.line_num}: {erro}.") from erro

    if not livros:
        raise ValueError("O CSV não contém livros.")
    return livros


def gravar_catalogo(livros: dict[str, Book]) -> tuple[int, int]:
    inseridos = 0
    capas_preenchidas = 0

    with Session(db.engine) as session:
        conexao = session.connection()
        conexao.exec_driver_sql("BEGIN IMMEDIATE")
        db.preparar_banco(conexao)
        consulta = select(GoodreadsBook.goodreads_id, Book).join(Book)
        existentes = dict(session.exec(consulta).all())

        for identificador, livro in livros.items():
            cadastrado = existentes.get(identificador)
            if cadastrado is not None:
                if cadastrado.capa_url is None and livro.capa_url is not None:
                    cadastrado.capa_url = livro.capa_url
                    capas_preenchidas += 1
                continue
            session.add(livro)
            # O flush obtém o ID interno sem confirmar a transação.
            session.flush()
            session.add(GoodreadsBook(goodreads_id=identificador, book_id=livro.id))
            inseridos += 1

        session.commit()

    return inseridos, capas_preenchidas


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Importa o catálogo limpo do Goodreads.")
    parser.add_argument("csv", type=Path, help="Caminho do arquivo CSV exportado.")
    parser.add_argument("--aplicar", action="store_true", help="Grava os livros no SQLite.")
    args = parser.parse_args(argv)

    try:
        livros = ler_catalogo(args.csv)
    except (OSError, ValueError, csv.Error) as erro:
        parser.exit(1, f"Erro no CSV: {erro}\n")

    print(f"Livros válidos no CSV: {len(livros)}.")
    if args.aplicar:
        db.engine.echo = False
        inseridos, capas_preenchidas = gravar_catalogo(livros)
        print(f"Inseridos: {inseridos}. Já cadastrados: {len(livros) - inseridos}.")
        print(f"Capas preenchidas em livros existentes: {capas_preenchidas}.")
        print(f"Banco: {db.DB_PATH}")
    else:
        print("Validação concluída. Use --aplicar para gravar no SQLite.")


if __name__ == "__main__":
    main()
