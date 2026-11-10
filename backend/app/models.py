from sqlmodel import SQLModel,Field

class Book (SQLModel,table = True):
    id:int | None = Field(default = None, primary_key = True)
    titulo: str
    autor:str
    ano_publicacao:int | None = None
    genero:str | None = None
    descricao:str
