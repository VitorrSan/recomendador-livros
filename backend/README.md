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

Consulta os livros cadastrados no SQLite e retorna uma lista em JSON.

Se o banco estiver vazio, a resposta será uma lista vazia: `[]`.

## 7. Testes automatizados

Executar na pasta `backend`:

`python -m pytest -v`

Testes existentes:

- `test_health.py`: verifica o endpoint `/health`.
- `test_books.py`: verifica a listagem utilizando um banco SQLite temporário.

Os testes não dependem de livros cadastrados no banco local do desenvolvedor.

## 8. Funcionalidades futuras

- Paginação e filtros no catálogo.
- Consulta de livros por ID.
- Importação do dataset definitivo.
- Integração com o Transformer.
- Endpoint de recomendações semânticas.
- Testes adicionais e hospedagem.

## 9. Observações

O projeto está em desenvolvimento acadêmico.

O Backend não depende de dados de exemplo fixados no código para iniciar.

O banco SQLite criado localmente não deve ser enviado ao GitHub.

Os integrantes devem utilizar o `requirements.txt` para instalar as dependências em seus próprios ambientes.