import re
from urllib.parse import urlsplit


def id_goodreads(url: str) -> str:
    endereco = urlsplit(url)
    caminho = re.fullmatch(r"/book/show/([1-9][0-9]*)(?:[-.][^/]+)?/?", endereco.path)
    if (
        endereco.scheme not in {"http", "https"}
        or endereco.hostname not in {"goodreads.com", "www.goodreads.com"}
        or caminho is None
    ):
        raise ValueError("a coluna 'url' deve identificar um livro no Goodreads")
    return caminho.group(1)
