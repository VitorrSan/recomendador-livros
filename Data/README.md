# Dados do catálogo e da recomendação

Obtenha com a equipe os três arquivos da mesma exportação e coloque-os nos caminhos abaixo, relativos à raiz do repositório.

| Arquivo | Caminho | Uso |
|---|---|---|
| Catálogo limpo | `Data/livros_limpos.csv` | Importa os livros e capas para o SQLite. |
| Metadados dos vetores | `backend/app/nlp/livros_metadata.csv` | Liga cada posição da matriz ao identificador Goodreads extraído da URL. |
| Matriz de embeddings | `backend/app/nlp/embeddings_livros.npy` | Contém os vetores usados para calcular a similaridade. |

O [notebook de limpeza](../Limpeza_de_dado.ipynb) prepara o primeiro CSV a partir da base Goodreads. O [notebook de embeddings](../02_embeddings_e_similaridade.ipynb) lê esse CSV e exporta os outros dois arquivos juntos. A coluna `book_id` dos metadados indica a posição na matriz. O Backend usa o ID Goodreads para localizar o livro no SQLite e devolver o ID interno da API.

## Conferir o lote validado

O lote validado tem 1.795 registros nos dois CSVs e uma matriz de 1.795 vetores com 384 dimensões. Na raiz do repositório, confira o SHA256 dos arquivos no PowerShell.

```powershell
$arquivos = @(
    '.\Data\livros_limpos.csv'
    '.\backend\app\nlp\livros_metadata.csv'
    '.\backend\app\nlp\embeddings_livros.npy'
)
Get-FileHash -LiteralPath $arquivos -Algorithm SHA256
```

| Arquivo | SHA256 do lote validado |
|---|---|
| `livros_limpos.csv` | `545348c8d224ff144c7e1fa962d9830d6a0b516dc667dfa6561ec43baf1db98d` |
| `livros_metadata.csv` | `b3735ad39a735e19903cb709390c6f934e860d272c391f00779c8e27f2280903` |
| `embeddings_livros.npy` | `dd36c4f3559bcafe068c8dc6e7dde7c7c5e5a9da9dbdf53626a81a3a7b4315d3` |

Depois da conferência, siga a [execução local do Backend](../backend/README.md#4-executar-a-aplicação). Para testar uma nova exportação, guarde juntos o catálogo, os metadados, a matriz e seus novos hashes. Importe em uma cópia separada com um banco novo e repita a conferência da API. A reimportação sobre um SQLite existente mantém registros antigos e preserva seus IDs.

## Regeneração no Colab

O notebook de limpeza usa nomes de colunas em inglês na exportação. Em uma sessão limpa, preserve esses nomes ao executar as células de limpeza, pois uma célula exploratória anterior os renomeia. No notebook de embeddings, a exportação ocorre antes da célula de carrinho, que ainda depende de uma função ausente. O lote validado pode ser usado diretamente, sem executar as células do Colab.
