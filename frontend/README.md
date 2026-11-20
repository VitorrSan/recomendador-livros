# EntreLivros — Frontend

Site em HTML, CSS e JavaScript puro, com tema preto, amarelo e madeira. Por padrão, carrega o catálogo e as recomendações da API FastAPI do projeto em `http://127.0.0.1:8000`.

- A tela inicial mostra um livro em destaque e fileiras por gênero com pelo menos três títulos. Quando não há gêneros com essa quantidade, mostra uma fileira geral.
- A busca sugere títulos e autores enquanto o usuário digita, com navegação pelo teclado e normalização de acentos.
- A página do livro mostra sinopse, autor, gênero, ano e capa, conforme os dados disponíveis, e consulta seus similares no Backend.
- Clicar em um livro da fileira ou dos similares abre seu detalhe. O botão voltar do navegador funciona e o endereço `#livro-ID` permite compartilhar a seleção.
- Quando a capa está ausente ou falha ao carregar, a interface apresenta o título sobre uma capa colorida.

A busca por título e autor usa os livros carregados no JavaScript. A recomendação usa o cosseno calculado pelo Backend a partir dos embeddings. A porcentagem exibida é o cosseno multiplicado por 100 e arredondado, como medida de proximidade entre vetores. Ela não representa a probabilidade de o usuário gostar do livro.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `index.html` | Estrutura da página e carregamento de `estilo.css` e dos scripts |
| `estilo.css` | Tema e layout responsivo |
| `script.js` | Requisições, fileiras, busca, detalhe e navegação |
| `config.js` | Endereço da API para desenvolvimento ou publicação |
| `dados.js` | Dados opcionais para o modo estático |

## Executar com o Backend

Prepare os dados, instale as dependências e inicie a API conforme o [guia do Backend](../backend/README.md). A propriedade `API_URL`, em `config.js`, aponta por padrão para `http://127.0.0.1:8000`.

Em outro PowerShell, abra a pasta `frontend` e inicie o servidor estático na porta 5173. Se o ambiente do Backend já estiver criado, use o comando abaixo.

```powershell
& ..\backend\.venv\Scripts\python.exe -m http.server 5173 --bind 127.0.0.1
```

Também é possível usar o Python instalado no Windows, com `py -m http.server 5173 --bind 127.0.0.1`. Abra [a interface local](http://127.0.0.1:5173).

O Backend permite as origens `http://localhost:5173` e `http://127.0.0.1:5173` por padrão. Caso a equipe utilize outra porta ou endereço, configure `CORS_ORIGINS` no PowerShell do Backend e reinicie a API, conforme o guia. Uma publicação da interface também precisa de um endereço de API acessível aos usuários e permitido nessa configuração.

## Usar a API no Railway

Primeiro conclua a configuração do volume e a importação do catálogo seguindo a seção de Railway no [guia do Backend](../backend/README.md). O sucesso de `/health` confirma que o processo responde; confira também um livro e suas recomendações antes de conectar a interface.

Depois, altere somente `API_URL` em `config.js` para `https://recomendador-livros-production.up.railway.app`. Esse arquivo é público e não deve conter senhas ou tokens. O restante do JavaScript usa o endereço configurado para consultar o catálogo e os similares.

Enquanto a interface estiver apenas no computador, mantenha as duas origens locais da porta 5173 no `CORS_ORIGINS` do Railway. Quando publicar o site, acrescente também sua origem HTTPS exata. O endereço da API e a origem do frontend têm funções diferentes: o primeiro é o destino das consultas; a segunda identifica o site autorizado a fazê-las pelo navegador.

## Contrato de integração

Na inicialização, `carregarLivros()` percorre `GET /books?offset=0&limit=100` e as páginas seguintes até receber uma página com menos de 100 itens. Isso disponibiliza o catálogo completo para as fileiras e a busca local.

Ao abrir um livro, o detalhe usa o registro já carregado. A interface solicita `GET /books/{id}/similar?limit=10` para receber até dez recomendações. A resposta é uma lista de objetos com `livro`, que contém os dados completos do recomendado, e `similaridade`, com o valor do cosseno. A navegação usa o ID interno devolvido em `livro.id`.

O adaptador de dados lê `capa_url` e `ano_publicacao` da API. Os campos `nota`, quantidade de avaliações, páginas, editora e URL externa são opcionais na interface. A API atual fornece o catálogo por gênero e o detalhe com os campos documentados no Backend. Se uma fonte de dados também fornecer notas e avaliações, a interface pode apresentar as fileiras "Mais bem avaliados" e "Mais populares" e escolher o destaque por nota. Sem esses campos, o destaque usa o primeiro livro do catálogo.

Se a resposta de similares for uma lista vazia, a página informa que não há similares cadastrados para aquele livro. Se a consulta falhar, mantém o detalhe e apresenta uma mensagem de erro na seção de recomendações.

## Modo estático opcional

Para usar somente dados locais, defina `API_URL: ""` em `config.js` e preencha `dados.js` com o objeto abaixo. O arquivo distribuído no repositório começa vazio. Todos os IDs usados em `similares` devem existir em `livros`.

```js
const DADOS = {
  livros: [
    { id: 1, titulo: "Livro A", autor: "Autor A", descricao: "Sinopse A." },
    { id: 2, titulo: "Livro B", autor: "Autor B", descricao: "Sinopse B." }
  ],
  similares: {
    1: [{ id: 2, score: 0.8 }],
    2: [{ id: 1, score: 0.8 }]
  }
};
```

Os campos opcionais e os nomes das colunas do dataset, como `title`, `author`, `book_cover` e `year`, também são aceitos pelo adaptador. Para testar esse modo, use o mesmo servidor estático descrito acima.

## Conferir a integração

- Carregar o catálogo e buscar três livros por título ou autor.
- Abrir um livro, conferir ano e capa e navegar para um dos similares.
- No lote validado, conferir *The House in the Cerulean Sea* com *Somewhere Beyond the Sea* como primeiro similar, próximo de 83%.
- Conferir a busca pelo teclado, o botão voltar e o layout no celular.
- Verificar a mensagem de indisponibilidade quando o serviço de recomendações falhar.
