from contextlib import asynccontextmanager
from os import getenv

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, col, select

from app.db import SQLITE_MAX_INTEGER, create_db_and_tables, get_session
from app.models import Book, GoodreadsBook, LivroSimilar
from app.nlp.recomendacoes import ArtefatosIndisponiveis, PASTA_ARTEFATOS, carregar_catalogo


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}



@router.get("/books", response_model=list[Book])
def listar_livros(
    offset: int = Query(default=0, ge=0, le=SQLITE_MAX_INTEGER),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    consulta = select(Book).order_by(Book.id).offset(offset).limit(limit)
    livros = session.exec(consulta).all()
    return livros


@router.get("/books/{book_id}", response_model=Book)
def buscar_livro(
    book_id: int = Path(ge=1, le=SQLITE_MAX_INTEGER),
    session: Session = Depends(get_session),
):
    livro = session.get(Book, book_id)

    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    return livro


@router.get("/books/{book_id}/similar", response_model=list[LivroSimilar])
def recomendar_livros_similares(
    book_id: int = Path(ge=1, le=SQLITE_MAX_INTEGER),
    limit: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session),
):
    buscar_livro(book_id, session)

    consulta = select(GoodreadsBook.goodreads_id, GoodreadsBook.book_id).join(Book)
    id_interno_por_goodreads = dict(session.exec(consulta).all())
    origem = next(
        (
            goodreads_id
            for goodreads_id, id_interno in id_interno_por_goodreads.items()
            if id_interno == book_id
        ),
        None,
    )
    if origem is None:
        return []

    try:
        catalogo = carregar_catalogo(PASTA_ARTEFATOS)
    except ArtefatosIndisponiveis as erro:
        raise HTTPException(status_code=503, detail="Recomendações indisponíveis") from erro

    disponiveis = {
        goodreads_id
        for goodreads_id, id_interno in id_interno_por_goodreads.items()
        if id_interno != book_id
    }
    ranking = catalogo.similares(origem, disponiveis, limit)
    ids_ranqueados = [id_interno_por_goodreads[goodreads_id] for goodreads_id, _ in ranking]
    if not ids_ranqueados:
        return []

    livros_por_id = {
        livro.id: livro
        for livro in session.exec(select(Book).where(col(Book.id).in_(ids_ranqueados))).all()
    }
    return [
        LivroSimilar(livro=livros_por_id[id_interno], similaridade=similaridade)
        for id_interno, (_, similaridade) in zip(ids_ranqueados, ranking)
        if id_interno in livros_por_id
    ]


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
