from fastapi import FastAPI, Query, Depends
from sqlmodel import Session, select
from app.db import engine, create_db_and_tables, get_session
from app.models import Book
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Recomendador Semântico de Livros",
    lifespan=lifespan
)


@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/books", response_model=list[Book])
def listar_livros(session: Session = Depends(get_session)):
    consulta = select(Book).order_by(Book.id)
    livros = session.exec(consulta).all()
    return livros
