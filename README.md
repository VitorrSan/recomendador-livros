# Recomendador Semântico de Livros

Sistema web de recomendação de livros utilizando Processamento de Linguagem Natural (PLN), modelos Transformers e similaridade do cosseno.

Projeto acadêmico desenvolvido por três integrantes com o objetivo de construir uma aplicação completa, integrando Front-end, Backend, dataset, banco de dados e um motor de recomendação semântica.

## 1. Sobre o projeto

O sistema permitirá que usuários pesquisem livros por meio de descrições escritas em linguagem natural, recebendo recomendações baseadas na similaridade semântica entre a consulta e as sinopses dos livros cadastrados.

**Exemplo de consulta:**

"Quero um livro de fantasia com dragões, magia, batalhas e reinos antigos."

O algoritmo deverá interpretar o significado dessa descrição e recomendar livros com conteúdos semanticamente relacionados, mesmo que não utilizem exatamente as mesmas palavras.

## 2. Objetivo

Desenvolver e disponibilizar uma aplicação web que utilize um Transformer pré-treinado para gerar representações vetoriais de textos (*embeddings*) e calcular a similaridade do cosseno entre consultas dos usuários e descrições dos livros.

### Funcionalidades previstas

- Pesquisa semântica de livros em linguagem natural.
- Geração de embeddings utilizando Sentence Transformers.
- Cálculo de similaridade do cosseno.
- Ranking dos livros mais relacionados à consulta.
- Exibição de título, autor, sinopse, gênero e capa.
- Catálogo de livros com paginação.
- Página de detalhes dos livros.
- API REST para comunicação entre Front-end e Backend.
- Tratamento de requisições inválidas e erros.

Funcionalidades adicionais poderão ser implementadas conforme a evolução do projeto.

## 3. Tecnologias previstas

| Camada | Tecnologia |
|---|---|
| Front-end | React, TypeScript e Vite |
| Estilização | Tailwind CSS |
| Backend | Python e FastAPI |
| Banco de dados | SQLite |
| ORM | SQLModel |
| PLN | Sentence Transformers |
| Similaridade | Similaridade do cosseno |
| Testes | pytest e HTTPX |
| Versionamento | Git e GitHub |

O modelo Transformer definitivo, o dataset e a plataforma de hospedagem ainda serão validados pelo grupo.

## 4. Arquitetura proposta

O fluxo de recomendação será:

1. O usuário escreve uma descrição do livro desejado.
2. O Front-end envia a consulta ao Backend.
3. O FastAPI valida os dados recebidos.
4. O serviço de PLN gera o embedding da consulta.
5. O algoritmo compara esse vetor com os embeddings dos livros.
6. A similaridade do cosseno permite ordenar os resultados.
7. O Backend recupera os metadados dos livros.
8. A API retorna as recomendações em formato JSON.
9. O Front-end apresenta os livros recomendados ao usuário.

Os embeddings dos livros poderão ser gerados previamente para otimizar as consultas.

## 5. Organização do repositório

```text
PLN/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .venv/             # Ambiente local, não versionado
├── frontend/
│   └── README.md
├── Data/
│   └── README.md
├── .gitignore
└── README.md
```

- **backend/**: API REST, banco de dados, integração com PLN e testes.
- **frontend/**: interface web e comunicação com a API.
- **Data/**: documentação e organização dos datasets utilizados.
- **README.md**: documentação geral do projeto.

A estrutura será ampliada conforme novas funcionalidades forem implementadas.

## 6. Equipe e responsabilidades

**Pessoa 1 — Front-end**

Desenvolvimento da interface, componentes visuais, páginas, formulários e integração com a API.

**Pessoa 2 — Dataset e Inteligência Artificial**

Seleção e tratamento dos dados, geração de embeddings, implementação do Transformer e algoritmo de recomendação.

**Pessoa 3 — Backend e Integração**

Desenvolvimento da API FastAPI, banco de dados, endpoints, integração com PLN, testes automatizados, documentação e deploy.

Todos os integrantes deverão compreender a arquitetura geral e contribuir para a integração e validação do projeto.

## 7. Preparação do ambiente Backend

As instruções abaixo consideram Windows com PowerShell e Python instalado.

### Criar o ambiente virtual

A partir da raiz do projeto:

```powershell
cd backend
py -m venv .venv
```

### Ativar o ambiente

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` deverá ser mantido atualizado conforme novas dependências forem adicionadas.

### Executar a API

Após a implementação da aplicação FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

A documentação interativa ficará disponível em:

`http://127.0.0.1:8000/docs`

**Observação:** a API ainda está em fase inicial de implementação. Estas instruções serão validadas e atualizadas à medida que os endpoints forem concluídos.

## 8. Organização do trabalho com Git

O projeto utilizará um repositório GitHub compartilhado entre os três integrantes.

Cada integrante deverá:

1. Clonar o repositório.
2. Configurar seu ambiente de desenvolvimento.
3. Criar uma branch para sua funcionalidade.
4. Implementar e testar as alterações.
5. Registrar commits com mensagens descritivas.
6. Enviar sua branch ao GitHub.
7. Abrir um Pull Request para integração na branch principal.

A branch `main` será utilizada como referência principal do projeto.

## 9. Dataset

O dataset definitivo ainda está em avaliação.

A fonte selecionada deverá disponibilizar metadados confiáveis dos livros e, principalmente, descrições textuais adequadas à busca semântica.

O grupo deverá verificar a qualidade dos dados, a presença de sinopses, as duplicatas e as condições de utilização da fonte.

## 10. Estado atual do desenvolvimento

**Em preparação:**

- Estrutura inicial do repositório.
- Ambiente Python do Backend.
- Configuração do FastAPI.
- Organização do fluxo de colaboração com GitHub.

**Próximas entregas:**

- Implementação e validação do endpoint `/health`.
- Configuração do banco SQLite.
- Criação dos endpoints de livros.
- Preparação do dataset e do modelo Transformer.
- Integração do algoritmo de recomendação.
- Desenvolvimento da interface React.
- Testes automatizados e hospedagem.

Este README será atualizado conforme o avanço das funcionalidades.

## 11. Contexto acadêmico

O projeto busca demonstrar a aplicação prática de modelos Transformers e da similaridade do cosseno em sistemas de recomendação.

Além do funcionamento da aplicação, o grupo deverá compreender e explicar as escolhas arquiteturais, o código desenvolvido, as limitações do modelo e o processo de integração entre os componentes.