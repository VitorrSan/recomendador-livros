# Recomendações semânticas

`recomendacoes.py` compara os embeddings dos livros e devolve o ranking por similaridade do cosseno. Use os dois arquivos exportados na mesma execução do notebook `02_embeddings_e_similaridade.ipynb`:

- `embeddings_livros.npy`
- `livros_metadata.csv`

Na execução local, coloque os arquivos nesta pasta antes de testar a rota de similares. A variável `NLP_ARTIFACTS_DIR` permite usar outro diretório sem mover o código. O catálogo limpo, os metadados e os vetores devem pertencer ao mesmo lote; confira os caminhos e hashes no [guia de dados](../../../Data/README.md).

No Railway, use `NLP_ARTIFACTS_DIR=/data/nlp` e guarde os dois arquivos no volume montado em `/data`:

- `/data/nlp/embeddings_livros.npy`
- `/data/nlp/livros_metadata.csv`

Os arquivos são enviados ao volume separadamente do código e continuam fora do commit. Não é necessário instalar o modelo Transformer ou gerar os vetores no servidor: a API utiliza os embeddings exportados pela equipe.

O carregamento ocorre na primeira consulta de similares e fica em memória. Reinicie o serviço ao substituir os arquivos. Artefatos ausentes ou inconsistentes produzem HTTP `503` na recomendação de um livro com vínculo Goodreads; isso não impede a consulta do catálogo.

Consulte o [guia de publicação no Railway](../../README.md#8-publicar-a-api-no-railway) para configurar o volume, transferir o lote, importar o catálogo e verificar as rotas. O mesmo README descreve o formato da resposta dos endpoints.
