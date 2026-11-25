from contextlib import asynccontextmanager
from itertools import batched
from os import getenv

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, col, select

from app.db import SQLITE_MAX_INTEGER, atualizar_banco, obter_sessao
from app.models import Book, GoodreadsBook, LivroSimilar
from app.nlp.recomendacoes import ArtefatosIndisponiveis, PASTA_ARTEFATOS, carregar_catalogo


@asynccontextmanager
async def lifespan(app: FastAPI):
    atualizar_banco()
    yield


router = APIRouter()
TAMANHO_LOTE_RECOMENDACOES = 64


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/books", response_model=list[Book])
def listar_livros(
    offset: int = Query(default=0, ge=0, le=SQLITE_MAX_INTEGER),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(obter_sessao),
):
    consulta = select(Book).order_by(Book.id).offset(offset).limit(limit)
    livros = session.exec(consulta).all()
    return livros


@router.get("/books/{book_id}", response_model=Book)
def buscar_livro(
    book_id: int = Path(ge=1, le=SQLITE_MAX_INTEGER),
    session: Session = Depends(obter_sessao),
):
    livro = session.get(Book, book_id)

    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    return livro


@router.get("/books/{book_id}/similar", response_model=list[LivroSimilar])
def recomendar_livros_similares(
    book_id: int = Path(ge=1, le=SQLITE_MAX_INTEGER),
    limit: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(obter_sessao),
):
    buscar_livro(book_id, session)

    origem = session.exec(
        select(GoodreadsBook.goodreads_id).where(GoodreadsBook.book_id == book_id)
    ).first()
    if origem is None:
        return []

    try:
        catalogo = carregar_catalogo(PASTA_ARTEFATOS)
    except ArtefatosIndisponiveis as erro:
        raise HTTPException(status_code=503, detail="Recomendações indisponíveis") from erro

    resultados = []
    for lote in batched(catalogo.iterar_similares(origem), TAMANHO_LOTE_RECOMENDACOES):
        ids_goodreads = [identificador for identificador, _ in lote]
        consulta = (
            select(GoodreadsBook.goodreads_id, Book)
            .join(Book)
            .where(
                col(GoodreadsBook.goodreads_id).in_(ids_goodreads),
                GoodreadsBook.book_id != book_id,
            )
        )
        livros_por_goodreads = dict(session.exec(consulta).all())
        for identificador, similaridade in lote:
            livro = livros_por_goodreads.get(identificador)
            if livro is not None:
                resultados.append(LivroSimilar(livro=livro, similaridade=similaridade))
                if len(resultados) == limit:
                    return resultados
    return resultados


def criar_app() -> FastAPI:
    api = FastAPI(title="Recomendador Semântico de Livros", lifespan=lifespan)
    origens = getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[origem.strip() for origem in origens.split(",") if origem.strip()],
        allow_methods=["GET"],
    )
    api.include_router(router)
    return api


app = criar_app()
