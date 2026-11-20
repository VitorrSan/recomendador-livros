# Backend — Recomendador Semântico de Livros

## 1. Sobre

Backend do projeto acadêmico de recomendação semântica de livros, desenvolvido com Python, FastAPI, SQLModel e SQLite.

A API disponibiliza o catálogo e recomenda livros semelhantes com os embeddings gerados previamente pela equipe.

## 2. Tecnologias

- Python 3.12
- FastAPI
- Uvicorn
- SQLModel e SQLAlchemy
- SQLite
- NumPy
- pytest
- HTTPX / HTTPX2

## 3. Preparação do ambiente

No Windows, instale o Python 3.12 e coloque os três arquivos do mesmo lote nos locais indicados no [guia de dados](../Data/README.md). Abra o PowerShell na raiz do repositório e execute os comandos abaixo. Execute os passos seguintes na pasta `backend`.

```powershell
Set-Location backend
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Selecionar o ambiente no VS Code:**

Abra a pasta do repositório no editor e use `Ctrl+Shift+P` → `Python: Select Interpreter` → `backend/.venv/Scripts/python.exe`.

O Python selecionado pelo editor deve ser o mesmo ambiente em que as dependências foram instaladas. Caso imports como `fastapi`, `sqlmodel` ou `pytest` apareçam como não encontrados, confira essa seleção antes de reinstalar pacotes. Ativar o ambiente no terminal não garante que o analisador do editor utilize o mesmo interpretador.

## 4. Executar a aplicação

Primeiro valide o CSV. Sem `--aplicar`, o comando confere o arquivo e mostra a quantidade de livros sem gravar no SQLite. Depois importe o catálogo e inicie a API.

```powershell
& .\.venv\Scripts\python.exe -m app.importar_catalogo ../Data/livros_limpos.csv
& .\.venv\Scripts\python.exe -m app.importar_catalogo ../Data/livros_limpos.csv --aplicar
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

O lote validado mostra 1.795 livros na validação e insere 1.795 livros em um banco novo. A API usa `http://127.0.0.1:8000`. Consulte ou teste as rotas na [documentação interativa](http://127.0.0.1:8000/docs).

### Conferir a instalação

Com a API em execução, abra outro PowerShell e consulte o primeiro livro do catálogo e seus similares.

```powershell
$api = 'http://127.0.0.1:8000'
Invoke-RestMethod "$api/health"
$primeiro = (Invoke-RestMethod "$api/books?limit=1")[0]
Invoke-RestMethod "$api/books/$($primeiro.id)"
Invoke-RestMethod "$api/books/$($primeiro.id)/similar?limit=3"
```

Em um banco novo com o lote validado, o detalhe é de *The House in the Cerulean Sea* e o primeiro similar é *Somewhere Beyond the Sea*, com cosseno próximo de `0.835`. Para reproduzir a instalação, repita os passos em uma cópia limpa com os três arquivos conferidos no [guia de dados](../Data/README.md).

### Conectar o frontend

Em desenvolvimento, as origens do frontend permitidas por padrão são `http://localhost:5173` e `http://127.0.0.1:5173`. A API oferece rotas HTTP de leitura por `GET`. Para autorizar outras origens, defina `CORS_ORIGINS` no mesmo PowerShell antes de iniciar a API. Informe origens completas com protocolo, host e porta, separadas por vírgula, sem caminhos ou barras finais.

```powershell
$env:CORS_ORIGINS = 'http://localhost:5174,http://127.0.0.1:5174'
```

A variável substitui a lista padrão. Inclua na configuração todas as origens que a equipe vai usar. Reinicie o servidor depois de alterar a variável.

## 5. Banco de dados

O banco utilizado nesta fase é SQLite.

O arquivo `books.db` é local e não deve ser versionado no GitHub.

Durante a inicialização da aplicação, a função `create_db_and_tables()` é chamada pelo mecanismo `lifespan` do FastAPI, criando as tabelas ausentes.

O cadastro de livros ocorre pelo importador. Em bancos criados antes do suporte a capas, a inicialização acrescenta a coluna opcional `capa_url` à tabela existente.

O modelo atual `Book` contém os campos:

- `id`
- `titulo`
- `autor`
- `ano_publicacao`
- `genero`
- `descricao`
- `capa_url`

### Importar o catálogo do Goodreads

O formato de entrada é CSV separado por vírgula, em UTF-8 com ou sem BOM. `title`, `author`, `description` e `url` são obrigatórios. `year`, `genre` e `book_cover` são opcionais. Anos inteiros exportados como `2024.0` são aceitos, e campos opcionais vazios são gravados como nulos. Quando preenchido, `book_cover` deve ser uma URL HTTP ou HTTPS.

O número em `goodreads.com/book/show/<id>-...` identifica o registro de origem. A tabela `GoodreadsBook` liga esse número ao ID gerado pelo SQLite. Um ID repetido com dados iguais no CSV representa um único livro. Dados divergentes para o mesmo ID interrompem a validação. Ao reaplicar o CSV, o importador só preenche a capa onde ainda estiver ausente em livros já cadastrados. Os IDs e os demais campos desses livros são preservados.

Para testar outro lote completo, use uma cópia separada do repositório com um `backend/books.db` novo. A reimportação é incremental e mantém os livros já cadastrados, inclusive os ausentes do novo CSV.

## 6. Endpoints implementados

**GET /health**

Verifica se a aplicação responde corretamente.

Resposta esperada: `{"status": "ok"}`

**GET /books**

Consulta os livros cadastrados no SQLite e retorna uma lista em JSON, ordenada por ID crescente e com paginação aplicada no banco de dados.

Parâmetros opcionais da consulta:

| Parâmetro | Padrão | Valores aceitos | Finalidade |
|---|---|---|---|
| `offset` | `0` | Inteiro entre zero e 2⁶³ − 1 | Quantidade de livros a pular |
| `limit` | `20` | Inteiro entre 1 e 100 | Quantidade máxima de livros a retornar |

Exemplos:

- `/books`: retorna até os primeiros 20 livros.
- `/books?offset=0&limit=20`: primeira página de até 20 livros.
- `/books?offset=20&limit=20`: segunda página de até 20 livros.
- `/books?offset=40&limit=20`: terceira página de até 20 livros.

Sem parâmetros, a listagem passa a retornar no máximo 20 livros. Para percorrer o catálogo, o Front-end deve aumentar o `offset` pelo `limit` utilizado.

Se o banco estiver vazio ou o `offset` estiver além dos registros disponíveis, a resposta será uma lista vazia: `[]`, com HTTP `200`. A última página pode conter menos livros que o `limit`.

Parâmetros inválidos, como `offset=-1`, `limit=0` ou `limit=101`, recebem HTTP `422` com detalhes da validação. A resposta continua sendo uma lista, sem metadados de total de livros ou páginas.

**GET /books/{book_id}**

Consulta um livro pela chave primária `id`. O parâmetro `book_id` faz parte do caminho e deve ser um inteiro entre 1 e 2⁶³ − 1.

Exemplo: `/books/7` procura o livro de ID `7`, independentemente da página em que ele apareça na listagem.

- Livro encontrado: HTTP `200` com um objeto JSON contendo `id`, `titulo`, `autor`, `ano_publicacao`, `genero`, `descricao` e `capa_url`. Quando não há capa cadastrada, `capa_url` vale `null`.
- ID válido, mas inexistente: HTTP `404` com `{"detail": "Livro não encontrado"}`. O mesmo ocorre se o catálogo estiver vazio.
- ID inválido, como `/books/abc`, `/books/1.5`, `/books/0` ou `/books/-1`: HTTP `422` com detalhes da validação.

A consulta utiliza `session.get(Book, book_id)` para buscar diretamente pela chave primária, sem carregar a lista de livros.

**GET /books/{book_id}/similar**

Retorna uma lista de recomendações ordenadas por similaridade do cosseno. Cada item tem `livro` (com os mesmos campos de `GET /books/{book_id}`) e `similaridade` (número de −1 a 1). O parâmetro `limit` aceita valores de 1 a 20, com padrão de 5. Exemplo: `/books/1/similar?limit=3`.

Coloque `embeddings_livros.npy` e `livros_metadata.csv`, exportados juntos pelo notebook da equipe, em `backend/app/nlp`. O CSV identifica a posição de cada vetor pela coluna `book_id` e o livro pela URL do Goodreads. O Backend cruza o ID Goodreads com o SQLite para devolver os IDs usados pela API.

Os arquivos são carregados e validados na primeira consulta de similares. Reinicie o servidor ao substituir os artefatos. A API responde com:

- HTTP `200` e uma lista de similares, sempre sem o próprio livro. A lista fica vazia se o livro existir mas não tiver vetor ou candidatos no catálogo.
- HTTP `404` se o livro não existir.
- HTTP `422` se o ID ou o limite for inválido.
- HTTP `503` se o livro tiver vínculo no catálogo e os artefatos para recomendar estiverem ausentes ou inválidos.

O frontend pode usar `GET /books?offset=0&limit=20` no catálogo e `GET /books/{id}` ao abrir um livro. Na mesma página, consulte `GET /books/{id}/similar` para obter os cards de recomendação. Use `livro.id` para abrir um card e preserve a ordem da resposta. Uma lista vazia indica que não há similares para exibir. Em caso de `503`, mantenha o detalhe do livro visível e apresente a indisponibilidade da recomendação. `capa_url` pode ser `null`.

## 7. Testes automatizados

Executar na pasta `backend`:

`& .\.venv\Scripts\python.exe -m pytest -v`

Testes existentes:

- `test_health.py`: verifica o endpoint `/health`.
- `test_books.py`: verifica catálogo vazio, listagem, paginação padrão, uso independente dos parâmetros, páginas ordenadas, limites aceitos e parâmetros inválidos, utilizando um banco SQLite temporário por teste.
- `test_importar_catalogo.py`: verifica validação do CSV, cadastro e reimportação em SQLite temporário.
- `test_recomendacoes.py`: verifica o vínculo por Goodreads, a ordem do ranking e as respostas quando faltam livros ou artefatos.
- `test_cors.py`: verifica as origens padrão, a configuração por variável e as regras para origens diferentes.

Os testes de livros também cobrem a consulta por ID: primeiro, intermediário e último livro do catálogo de teste, incluindo um livro fora da primeira página; resposta completa; ID inexistente; catálogo vazio; e IDs inválidos.

Os testes não dependem de livros cadastrados no banco local do desenvolvedor.

## 8. Funcionalidades futuras

- Filtros no catálogo.
- Validação do fluxo completo com a interface.
- Busca semântica por texto.
- Testes adicionais e hospedagem.

## 9. Observações

O projeto está em desenvolvimento acadêmico.

O Backend não depende de dados de exemplo fixados no código para iniciar.

O banco SQLite criado localmente não deve ser enviado ao GitHub.

Os integrantes devem utilizar o `requirements.txt` para instalar as dependências em seus próprios ambientes.
