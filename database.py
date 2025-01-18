import logging
import os
import sqlite3

from dotenv import load_dotenv
from sqlalchemy import Engine, event
from sqlmodel import Session, SQLModel, create_engine

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurar o logger
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

# Configuração do banco de dados
engine = create_engine(os.getenv("DATABASE_URL"))


# Criar a(s) tabela(s) no banco de dados
# Inicializa o banco de dados
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:  # somente para o SQLite
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()
