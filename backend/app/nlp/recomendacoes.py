import csv
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from itertools import islice
from os import getenv
from pathlib import Path
from zipfile import BadZipFile

import numpy as np

from app.goodreads import id_goodreads


PASTA_ARTEFATOS = Path(
    getenv("NLP_ARTIFACTS_DIR") or Path(__file__).resolve().parent
).expanduser().resolve()


class ArtefatosIndisponiveis(Exception):
    """Os arquivos necessários ao ranking estão ausentes ou inconsistentes."""


@dataclass(frozen=True)
class CatalogoVetorial:
    vetores: np.ndarray
    ids_por_posicao: tuple[str, ...]
    posicao_por_id: dict[str, int]

    def similares(
        self,
        origem: str,
        disponiveis: set[str],
        limite: int,
    ) -> list[tuple[str, float]]:
        candidatos = (
            (identificador, score)
            for identificador, score in self.iterar_similares(origem)
            if identificador in disponiveis
        )
        return list(islice(candidatos, limite))

    def iterar_similares(self, origem: str) -> Iterator[tuple[str, float]]:
        posicao = self.posicao_por_id.get(origem)
        if posicao is None:
            return

        # O produto escalar entre vetores de norma 1 é o cosseno.
        pontuacoes = np.clip(self.vetores @ self.vetores[posicao], -1.0, 1.0)
        ordem = np.argsort(-pontuacoes, kind="stable")
        for indice in ordem:
            candidato = self.ids_por_posicao[indice]
            if candidato != origem:
                yield candidato, float(pontuacoes[indice])


def ler_ids_por_posicao(caminho: Path, quantidade: int) -> tuple[str, ...]:
    por_posicao: dict[int, str] = {}
    ids: set[str] = set()

    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        colunas = leitor.fieldnames or []
        if not {"book_id", "url"}.issubset(colunas) or len(colunas) != len(set(colunas)):
            raise ValueError("Os metadados precisam das colunas únicas book_id e url.")

        for linha in leitor:
            if None in linha or any(valor is None for valor in linha.values()):
                raise ValueError(f"Linha {leitor.line_num} dos metadados incompleta ou excedente.")
            posicao = int(linha["book_id"])
            identificador = id_goodreads(linha["url"].strip())
            if not 0 <= posicao < quantidade or posicao in por_posicao:
                raise ValueError(f"Posição de embedding inválida ou repetida: {posicao}.")
            if identificador in ids:
                raise ValueError(f"ID Goodreads repetido nos metadados: {identificador}.")

            por_posicao[posicao] = identificador
            ids.add(identificador)

    if len(por_posicao) != quantidade:
        raise ValueError("A quantidade de vetores difere da quantidade de livros nos metadados.")
    return tuple(por_posicao[posicao] for posicao in range(quantidade))


@lru_cache(maxsize=1)
def carregar_catalogo(pasta: Path) -> CatalogoVetorial:
    try:
        with (pasta / "embeddings_livros.npy").open("rb") as arquivo:
            vetores = np.load(arquivo, allow_pickle=False)
            if not isinstance(vetores, np.ndarray):
                vetores.close()
                raise ValueError("O arquivo NPY precisa conter uma matriz.")

        if (
            vetores.ndim != 2
            or not vetores.size
            or not np.issubdtype(vetores.dtype, np.floating)
            or not np.isfinite(vetores).all()
        ):
            raise ValueError("Os embeddings precisam formar uma matriz numérica finita.")

        with np.errstate(over="ignore", under="ignore"):
            normas = np.linalg.norm(vetores, axis=1)
        if not np.isfinite(normas).all() or np.any(normas == 0):
            raise ValueError("Os embeddings precisam ter normas finitas e positivas.")

        ids = ler_ids_por_posicao(pasta / "livros_metadata.csv", vetores.shape[0])
        return CatalogoVetorial(
            vetores=vetores / normas[:, None],
            ids_por_posicao=ids,
            posicao_por_id={identificador: indice for indice, identificador in enumerate(ids)},
        )
    except (OSError, ValueError, EOFError, OverflowError, BadZipFile, csv.Error) as erro:
        raise ArtefatosIndisponiveis(str(erro)) from erro
