# Front-end: biblioteca de livros parecidos (similaridade do cosseno)

Site estático (HTML, CSS e JavaScript puro, sem instalar nada), com tema preto e
detalhes de biblioteca (amarelo e madeira).

- **Tela inicial:** fileiras de livros estilo Netflix ("Mais bem avaliados", "Mais populares" e uma por gênero).
- **Destaque:** o livro mais bem avaliado aparece em evidência no topo.
- **"Mais bem avaliados"** só considera livros com avaliações suficientes (ignora os 25% com menos `avaliacoes`), para um livro com nota 5,0 e 3 votos não ficar na frente de livros avaliados por milhões de pessoas.
- **Busca:** o usuário digita um livro, escolhe nas sugestões e vê o livro com a lista dos mais parecidos e a % de similaridade.
- **Clicar** em qualquer livro (fileira ou lista) abre a página dele. O botão voltar do navegador funciona e o link `#livro-ID` pode ser compartilhado.

O front **não calcula a similaridade**: ele só exibe o `score` que o back entrega.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `index.html` | Estrutura da página |
| `style.css` | Visual (tema preto, responsivo) |
| `script.js` | Fileiras, busca, página do livro, navegação |
| `dados.js` | **Vazio.** Aqui entram os dados reais (formato abaixo) |

## Como rodar

Abra o `index.html` no navegador (dois cliques). Não precisa de servidor. Com o `dados.js` vazio, o site mostra um aviso na tela inicial.
Para o modo API (abaixo), use um servidor local, por exemplo o Live Server do VS Code.

## Formato dos dados

```js
const DADOS = {
  livros: [
    { id: 0, titulo: "The Midnight Library", autor: "Matt Haig", ano: 2020, genero: "Fiction",
      capa: "https://...", nota: 3.98, avaliacoes: 2528798, paginas: 288, editora: "Viking",
      descricao: "Between life and death there is a library...", url: "https://www.goodreads.com/book/show/..." }
  ],
  similares: {
    0: [ { id: 7, score: 0.91 }, { id: 3, score: 0.62 } ]
  }
};
```

- Só `id` e `titulo` são obrigatórios. Os outros campos são opcionais (o que faltar simplesmente não aparece).
- `score` = similaridade do cosseno de 0 a 1 (também aceita 0 a 100). Guardar os top 10 de cada livro.
- Todos os ids de `similares` precisam existir em `livros`.
- `capa` precisa ser um link `https://`. Sem capa (ou com link quebrado), o site desenha uma capa com o título.
- `genero` com **um** valor por livro (se vier lista, usa o primeiro). Gêneros com menos de 3 livros não viram fileira.
- `descricao` aparece na página do livro (o front mostra até 600 caracteres, então vale cortar no export para o arquivo não ficar pesado). `url` vira o link "Ver no Goodreads".
- O front também aceita direto os nomes das colunas do dataset (`title`, `author`, `book_cover`, `avg_rating`, `num_ratings`, `year`, `genre`, `pages`, `publisher`, `description`, `url`). Se `id` faltar, usa a posição do livro.

## Exportar do notebook (pandas) para o `dados.js`

No fim do notebook de embeddings, onde `df` é o DataFrame limpo e `sim` é a matriz
de similaridade do cosseno (`cosine_similarity(embeddings)`), na **mesma ordem** das linhas do `df`:

```python
import json, numpy as np, pandas as pd

TOP = 10
def v(x): return None if pd.isna(x) else x
def inteiro(x): return None if pd.isna(x) else int(x)
def texto(x, n=600): return None if pd.isna(x) else str(x)[:n]

d = df.reset_index(drop=True)
livros = [{"id": int(i), "titulo": r["title"], "autor": v(r["author"]), "ano": inteiro(r["year"]),
           "genero": v(r["genre"]), "capa": v(r["book_cover"]), "nota": v(r["avg_rating"]),
           "avaliacoes": inteiro(r["num_ratings"]), "paginas": inteiro(r["pages"]), "editora": v(r["publisher"]),
           "descricao": texto(r["description"]), "url": v(r["url"])}
          for i, r in d.iterrows()]

similares = {}
for i in range(len(d)):
    ordem = [j for j in np.argsort(-sim[i]) if j != i][:TOP]
    similares[i] = [{"id": int(j), "score": round(float(sim[i][j]), 4)} for j in ordem]

with open("dados.js", "w", encoding="utf-8") as f:
    f.write("const DADOS = " + json.dumps({"livros": livros, "similares": similares}, ensure_ascii=False) + ";")
```

Depois é só colocar o `dados.js` gerado dentro da pasta `frontend/`, no lugar do vazio. Ao abrir o site, aperte F12 e veja o console: ele avisa se houver livros sem parecidos, ids que não existem ou ids repetidos.

## Se preferirem uma API

Em `script.js`, preencher `API_URL` no topo. A API precisa ter:

- `GET /livros` retornando a mesma lista de `livros` acima
- `GET /similares/{id}` retornando `[{ "id": 2, "score": 0.91 }]`
- CORS liberado, senão o navegador bloqueia a chamada.

## Checklist antes da entrega

- [ ] `dados.js` trocado pelos dados reais (ou `API_URL` preenchido)
- [ ] Buscar 3 livros e conferir se os parecidos fazem sentido
- [ ] Testar no celular
- [ ] Site publicado e link funcionando

## Publicar

- **GitHub Pages:** Settings → Pages → escolher a branch e a pasta onde está o `index.html`.
- **Netlify:** arrastar a pasta no painel do Netlify, ou conectar o repositório.
