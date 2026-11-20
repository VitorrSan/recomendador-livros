from os import getenv
from pathlib import Path

from sqlalchemy import Connection, event, inspect
from sqlmodel import SQLModel, Session, create_engine

from app import models


# Localização do banco
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(getenv("BOOKS_DB_PATH") or BASE_DIR / "books.db").expanduser().resolve()
SQLITE_MAX_INTEGER = 2**63 - 1

# Configuração do SQLite
sqlite_url = f"sqlite:///{DB_PATH.as_posix()}"

sql_echo = getenv("SQL_ECHO", "").strip().lower() in {"1", "true", "yes", "on"}
engine = create_engine(sqlite_url, echo=sql_echo)


@event.listens_for(engine, "do_connect")
def preparar_pasta_banco(_dialeto, _registro, _argumentos, _parametros):
    # API e importador criam a pasta somente quando vão abrir o banco.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@event.listens_for(engine, "connect")
def habilitar_chaves_estrangeiras(conexao, _registro):
    conexao.execute("PRAGMA foreign_keys=ON").close()


def preparar_banco(conexao: Connection):
    SQLModel.metadata.create_all(conexao)

    # Bancos antigos precisam da coluna nova antes de consultar Book.
    colunas = inspect(conexao).get_columns(models.Book.__tablename__)
    if all(coluna["name"] != "capa_url" for coluna in colunas):
        conexao.exec_driver_sql("ALTER TABLE book ADD COLUMN capa_url VARCHAR")


def create_db_and_tables():
    with engine.begin() as conexao:
        conexao.exec_driver_sql("BEGIN IMMEDIATE")
        preparar_banco(conexao)


# Fornecimento de sessões para a API
def get_session():
    with Session(engine) as session:
        yield session
