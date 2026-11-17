from sqlmodel import SQLModel,Field

class Book (SQLModel,table = True):
    id:int | None = Field(default = None, primary_key = True)
    titulo: str
    autor:str
    ano_publicacao:int | None = None
    genero:str | None = None
    descricao:str
    capa_url: str | None = None


class GoodreadsBook(SQLModel, table=True):
    goodreads_id: str = Field(primary_key=True)
    book_id: int = Field(foreign_key="book.id")
