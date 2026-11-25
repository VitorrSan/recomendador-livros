from alembic import context
from sqlalchemy import Connection
from sqlmodel import SQLModel

from app import db, models  # Os modelos registram as tabelas no SQLModel.metadata.


def executar_migracoes(conexao: Connection) -> None:
    context.configure(connection=conexao, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("As migrações precisam inspecionar um banco SQLite existente ou vazio.")

conexao_compartilhada = context.config.attributes.get("connection")
if conexao_compartilhada is not None:
    executar_migracoes(conexao_compartilhada)
else:
    with db.engine.begin() as conexao:
        conexao.exec_driver_sql("BEGIN IMMEDIATE")
        executar_migracoes(conexao)
