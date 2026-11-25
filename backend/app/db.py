from os import getenv
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, event
from sqlmodel import Session, create_engine


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
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.attributes["connection"] = conexao
    command.upgrade(config, "head")


def atualizar_banco():
    with engine.begin() as conexao:
        conexao.exec_driver_sql("BEGIN IMMEDIATE")
        preparar_banco(conexao)


# Fornecimento de sessões para a API
def obter_sessao():
    with Session(engine) as session:
        yield session
