# Backend — Recomendador Semântico de Livros

## 1. Sobre

Backend do projeto acadêmico de recomendação semântica de livros, desenvolvido com Python, FastAPI, SQLModel e SQLite.

Este módulo será responsável por disponibilizar os dados dos livros e integrar futuramente o algoritmo de recomendação semântica.

## 2. Tecnologias

- Python 3.12
- FastAPI
- Uvicorn
- SQLModel e SQLAlchemy
- SQLite
- pytest
- HTTPX / HTTPX2

## 3. Preparação do ambiente

Os comandos devem ser executados no PowerShell, a partir da pasta `backend`.

**Criar o ambiente virtual:**

`py -3.12 -m venv .venv`

**Ativar o ambiente:**

`.\.venv\Scripts\Activate.ps1`

**Instalar dependências:**

`python -m pip install -r requirements.txt`

**Selecionar o ambiente no VS Code:**

Abra a pasta do repositório no editor e use `Ctrl+Shift+P` → `Python: Select Interpreter` → `backend/.venv/Scripts/python.exe`.

O Python selecionado pelo editor deve ser o mesmo ambiente em que as dependências foram instaladas. Caso imports como `fastapi`, `sqlmodel` ou `pytest` apareçam como não encontrados, confira essa seleção antes de reinstalar pacotes. Ativar o ambiente no terminal não garante que o analisador do editor utilize o mesmo interpretador.

## 4. Executar a aplicação

`python -m uvicorn app.main:app --reload`

A API estará disponível em:

`http://127.0.0.1:8000`

Documentação interativa:

`http://127.0.0.1:8000/docs`

## 5. Banco de dados

O banco utilizado nesta fase é SQLite.

O arquivo `books.db` é local e não deve ser versionado no GitHub.

Durante a inicialização da aplicação, a função `create_db_and_tables()` é chamada pelo mecanismo `lifespan` do FastAPI, criando as tabelas ausentes.

Essa inicialização não cadastra livros automaticamente e não realiza migrações em tabelas existentes.

O modelo atual `Book` contém os campos:

- `id`
- `titulo`
- `autor`
- `ano_publicacao`
- `genero`
- `descricao`

O modelo poderá ser expandido após a definição do dataset definitivo.

## 6. Endpoints implementados

**GET /health**

Verifica se a aplicação responde corretamente.

Resposta esperada: `{"status": "ok"}`

**GET /books**

Consulta os livros cadastrados no SQLite e retorna uma lista em JSON, ordenada por ID crescente e com paginação aplicada no banco de dados.

Parâmetros opcionais da consulta:

| Parâmetro | Padrão | Valores aceitos | Finalidade |
|---|---|---|---|
| `offset` | `0` | Inteiro maior ou igual a zero | Quantidade de livros a pular |
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

Consulta um livro pela chave primária `id`. O parâmetro `book_id` faz parte do caminho e deve ser um inteiro maior ou igual a 1.

Exemplo: `/books/7` procura o livro de ID `7`, independentemente da página em que ele apareça na listagem.

- Livro encontrado: HTTP `200` com um objeto JSON contendo `id`, `titulo`, `autor`, `ano_publicacao`, `genero` e `descricao`.
- ID válido, mas inexistente: HTTP `404` com `{"detail": "Livro não encontrado"}`. O mesmo ocorre se o catálogo estiver vazio.
- ID inválido, como `/books/abc`, `/books/1.5`, `/books/0` ou `/books/-1`: HTTP `422` com detalhes da validação.

A consulta utiliza `session.get(Book, book_id)` para buscar diretamente pela chave primária, sem carregar a lista de livros.

## 7. Testes automatizados

Executar na pasta `backend`:

`python -m pytest -v`

Testes existentes:

- `test_health.py`: verifica o endpoint `/health`.
- `test_books.py`: verifica catálogo vazio, listagem, paginação padrão, uso independente dos parâmetros, páginas ordenadas, limites aceitos e parâmetros inválidos, utilizando um banco SQLite temporário por teste.

Os testes de livros também cobrem a consulta por ID: primeiro, intermediário e último livro do catálogo de teste, incluindo um livro fora da primeira página; resposta completa; ID inexistente; catálogo vazio; e IDs inválidos.

Os testes não dependem de livros cadastrados no banco local do desenvolvedor.

## 8. Funcionalidades futuras

- Filtros no catálogo.
- Importação do dataset definitivo.
- Integração com o Transformer.
- Endpoint de recomendações semânticas.
- Testes adicionais e hospedagem.

## 9. Observações

O projeto está em desenvolvimento acadêmico.

O Backend não depende de dados de exemplo fixados no código para iniciar.

O banco SQLite criado localmente não deve ser enviado ao GitHub.

Os integrantes devem utilizar o `requirements.txt` para instalar as dependências em seus próprios ambientes.
