from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    ano_publicacao: int | None = None
    genero: str | None = None
    descricao: str
    capa_url: str | None = None
    nota: float | None = None
    avaliacoes: int | None = None
    paginas: int | None = None
    editora: str | None = None
    url: str | None = None


class GoodreadsBook(SQLModel, table=True):
    goodreads_id: str = Field(primary_key=True)
    # Cada livro interno tem no máximo um vínculo com o Goodreads.
    book_id: int = Field(foreign_key="book.id", unique=True, index=True)


class LivroSimilar(SQLModel):
    livro: Book
    similaridade: float
