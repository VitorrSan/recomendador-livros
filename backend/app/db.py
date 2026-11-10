
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

from app import models


# Localização do banco
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "books.db"

# Configuração do SQLite
sqlite_url = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(sqlite_url, echo=True)


# Criação das tabelas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Fornecimento de sessões para a API
def get_session():
    with Session(engine) as session:
        yield session
