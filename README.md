# Recomendador Semântico de Livros

**Sistema Web de Recomendação de Livros utilizando Transformers, Processamento de Linguagem Natural e Similaridade do Cosseno.**

## 1. Sobre o Projeto

O projeto consiste no desenvolvimento de uma plataforma web de recomendação inteligente de livros, inspirada na experiência de descoberta de conteúdos de plataformas como Netflix e Amazon.

O sistema permite explorar o catálogo, buscar por título ou autor, consultar informações sobre as obras e receber recomendações de títulos semelhantes ao livro selecionado.

Além da recomendação baseada nas características dos livros, o projeto prevê a possibilidade de personalização das sugestões conforme os interesses e as interações de cada usuário.

Para realizar as recomendações, utilizaremos técnicas de Processamento de Linguagem Natural (PLN), modelos Transformers pré-treinados, embeddings textuais e similaridade do cosseno.

Como funcionalidade complementar, o sistema poderá permitir pesquisas semânticas por descrições escritas em linguagem natural.

O objetivo é desenvolver uma aplicação funcional, integrando Front-end, Backend, banco de dados, dataset e algoritmos de Inteligência Artificial, demonstrando a aplicação prática de Transformers em sistemas de recomendação.

## 2. Objetivo

Desenvolver um sistema web capaz de recomendar livros de maneira inteligente, utilizando similaridade semântica entre obras e, progressivamente, informações sobre as preferências dos usuários.

O sistema deverá permitir:

- Navegar por um catálogo de livros.
- Consultar os detalhes de uma obra.
- Receber recomendações de livros semelhantes ao título selecionado.
- Visualizar informações como título, autor, sinopse, gênero, capa e ano de publicação.
- Explorar recomendações organizadas em uma interface intuitiva e responsiva.
- Futuramente, receber sugestões personalizadas conforme preferências e interações.
- Como funcionalidade adicional, pesquisar livros por meio de descrições em linguagem natural.

## 3. Funcionalidades do Sistema

### 3.1. Recomendação de livros semelhantes — Funcionalidade principal

O usuário poderá selecionar um livro do catálogo e receber recomendações de outros títulos semanticamente relacionados.

No lote atual, ao selecionar *The House in the Cerulean Sea*, a API recomenda *Somewhere Beyond the Sea* em primeiro lugar. O sistema compara o embedding da obra selecionada com os vetores dos demais livros e ordena os resultados pelo cosseno.

As recomendações poderão ser apresentadas em uma seção denominada **"Você também pode gostar"**.

O algoritmo utilizará características textuais dos livros para identificar relações semânticas, não dependendo exclusivamente de palavras idênticas ou da classificação por gênero.

### 3.2. Recomendações personalizadas por usuário — Funcionalidade planejada

O sistema poderá permitir que usuários possuam perfis individuais, possibilitando recomendações adaptadas aos seus interesses.

Entre as interações consideradas estão:

- Livros visualizados.
- Livros adicionados aos favoritos.
- Gêneros de interesse.
- Livros avaliados, caso essa funcionalidade seja implementada.
- Histórico de interações com o catálogo.

**Exemplo:**

Um usuário demonstra interesse frequente por livros de romance e fantasia.

A partir dessas informações, o sistema poderá construir um perfil de preferências e recomendar livros semanticamente relacionados aos interesses identificados.

Uma abordagem inicial será utilizar embeddings dos livros com os quais o usuário interagiu para construir um vetor representativo de seus interesses.

Esse vetor poderá ser comparado aos embeddings dos livros disponíveis por meio da similaridade do cosseno.

A personalização será desenvolvida progressivamente, conforme a disponibilidade de dados, o tempo do projeto e a viabilidade técnica.

O sistema não pressupõe que a visualização de um livro, isoladamente, represente uma preferência positiva. Diferentes tipos de interação poderão receber pesos distintos.

### 3.3. Busca semântica por linguagem natural — Funcionalidade complementar

O sistema também poderá oferecer uma ferramenta de pesquisa em que o usuário descreve o tipo de livro que deseja encontrar.

**Exemplo:**

"Quero um livro de fantasia com dragões, magia e uma grande aventura."

O Transformer gerará um embedding da consulta, que será comparado aos embeddings das descrições dos livros.

O sistema retornará os títulos semanticamente mais próximos da descrição, mesmo quando não houver correspondência exata entre as palavras utilizadas.

Essa funcionalidade utilizará a mesma base tecnológica empregada nas recomendações por similaridade entre livros.

### 3.4. Catálogo e navegação

A aplicação deverá disponibilizar um catálogo contendo os livros cadastrados no sistema.

Funcionalidades previstas:

- Listagem paginada.
- Cards com informações dos livros.
- Página individual de detalhes.
- Navegação entre livros relacionados.
- Organização visual inspirada em plataformas de descoberta de conteúdos.
- Filtros por gênero ou outras características, conforme disponibilidade dos dados.

## 4. Tecnologias

| Camada | Tecnologia |
|---|---|
| Front-end | HTML, CSS e JavaScript |
| Estilização | CSS responsivo |
| Backend | Python e FastAPI |
| Banco de dados inicial | SQLite |
| Modelagem e ORM | SQLModel / SQLAlchemy |
| PLN | Sentence Transformers |
| Modelo de IA do lote atual | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Representação textual | Embeddings |
| Comparação vetorial | Similaridade do cosseno |
| Processamento numérico | NumPy / PyTorch |
| Testes | pytest e clientes HTTP |
| Versionamento | Git e GitHub |
| Hospedagem da API | Railway, com SQLite e vetores em volume persistente |
| Hospedagem da interface | GitHub Pages, com publicação preparada por GitHub Actions |

As tecnologias são escolhas iniciais e poderão ser ajustadas conforme as necessidades de integração e hospedagem.

## 5. Funcionamento do Algoritmo

### 5.1. Representação semântica dos livros

As sinopses e outras informações textuais relevantes serão preparadas e processadas por um modelo Transformer pré-treinado.

O modelo converterá os textos em embeddings, que são representações numéricas capazes de capturar características semânticas.

Os notebooks pré-calculam os embeddings. A API carrega a matriz e os metadados exportados e reutiliza os vetores para responder às consultas.

### 5.2. Similaridade do cosseno

A similaridade entre dois livros será calculada utilizando seus respectivos vetores.

A fórmula utilizada é:

**similaridade(A, B) = (A · B) / (||A|| × ||B||)**

Em que:

- A representa o vetor do livro selecionado.
- B representa o vetor de outro livro.
- A · B representa o produto escalar.
- ||A|| e ||B|| representam as normas dos vetores.

Os livros serão ordenados conforme a pontuação de similaridade obtida.

O livro utilizado como referência será excluído do próprio ranking de recomendações.

A pontuação representa proximidade entre embeddings, não a probabilidade de o usuário gostar de determinado livro.

### 5.3. Personalização das recomendações

Em uma etapa posterior, o sistema poderá utilizar as interações dos usuários para construir perfis de interesses.

Uma implementação inicial poderá combinar embeddings dos livros associados ao usuário, considerando pesos diferentes para determinados tipos de interação.

O vetor resultante representará os interesses estimados do usuário e poderá ser comparado aos embeddings do catálogo.

Essa abordagem permitirá desenvolver uma personalização baseada em conteúdo sem exigir, inicialmente, um grande volume de avaliações de diferentes usuários.

Abordagens de filtragem colaborativa poderão ser estudadas futuramente, caso exista quantidade suficiente de dados de interação.

## 6. Arquitetura do Sistema

A aplicação será organizada em componentes responsáveis por diferentes etapas do processamento.

### Front-end

Responsável pela interface web, navegação pelo catálogo, visualização dos livros e apresentação das recomendações.

### Backend

Responsável por disponibilizar a API REST, validar requisições, consultar o banco de dados e integrar o serviço de recomendação.

### Banco de dados

Responsável por armazenar os metadados dos livros.

Caso a personalização seja implementada, o esquema poderá ser ampliado para armazenar usuários, favoritos e interações.

### Serviço de PLN

Responsável pela geração de embeddings, cálculo de similaridades e organização do ranking de recomendações.

### Fluxo de recomendação entre livros

1. O usuário seleciona um livro no Front-end.
2. O Front-end envia o ID do livro ao Backend.
3. O FastAPI valida a requisição.
4. O serviço de recomendação recupera o embedding correspondente ao livro selecionado.
5. A similaridade do cosseno compara esse vetor aos demais embeddings.
6. O algoritmo ordena os livros por similaridade e exclui o livro de referência.
7. O Backend consulta o banco para recuperar os metadados.
8. A API retorna os resultados em JSON.
9. O Front-end apresenta as recomendações ao usuário.

## 7. Dataset

O lote validado tem 1.795 livros do Goodreads. O importador cria o catálogo no SQLite e mantém o vínculo entre o ID de origem do Goodreads e o ID interno usado pela API. Os notebooks preparam o CSV e geram os embeddings de 384 dimensões.

Para reproduzir o catálogo e o ranking, use os três arquivos do mesmo lote e confira os locais e hashes no [guia de dados](Data/README.md).

## 8. Endpoints da API

### Implementados no Backend

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/health` | Verificar a resposta da aplicação |
| GET | `/books` | Listar livros com paginação |
| GET | `/books/{book_id}` | Consultar um livro pelo ID |
| GET | `/books/{book_id}/similar` | Recomendar livros semelhantes ao selecionado |

O Backend utiliza SQLite e SQLModel e prepara as tabelas na inicialização. Para abrir um resultado de recomendação, o frontend usa o ID interno retornado em `livro.id`. O contrato de resposta e as origens permitidas para desenvolvimento estão no [guia do Backend](backend/README.md).

### Planejados

| Método | Endpoint sugerido | Finalidade |
|---|---|---|
| POST | `/recommendations/search` | Busca semântica por texto |
| GET | `/users/me/recommendations` | Recomendações personalizadas ao usuário autenticado |
| POST | `/interactions` | Registrar interações relevantes para personalização |

Os endpoints planejados são propostas de contrato e poderão ser ajustados após discussão entre os integrantes.

As rotas relacionadas a usuários dependerão da definição de autenticação, privacidade e armazenamento das interações.

## 9. Divisão de Responsabilidades

O projeto será desenvolvido por três integrantes.

### Pessoa 1 — Front-end

Responsável por:

- Interface do catálogo.
- Cards e páginas de detalhes dos livros.
- Componentes de recomendação.
- Navegação e responsividade.
- Comunicação com a API.
- Interface de perfil e preferências, caso implementada.

### Pessoa 2 — Dataset e Inteligência Artificial

Responsável por:

- Escolha e preparação do dataset.
- Limpeza e padronização das descrições.
- Seleção do Transformer.
- Geração dos embeddings.
- Cálculo da similaridade do cosseno.
- Ranking de livros semelhantes.
- Lógica de personalização baseada em conteúdo, em colaboração com o Backend.
- Avaliação da qualidade das recomendações.

### Pessoa 3 — Backend, Banco de Dados e Integração

Responsável por:

- Configuração da aplicação FastAPI.
- Modelagem e gerenciamento do banco.
- Endpoints do catálogo.
- Integração com o módulo de recomendação.
- Preservação da correspondência entre IDs e embeddings.
- Endpoints de recomendações.
- Persistência de usuários e interações, caso implementada.
- Validação de requisições e tratamento de erros.
- Testes automatizados.
- Documentação e deploy do Backend.

Todos os integrantes deverão compreender o funcionamento geral da aplicação para a apresentação e arguição acadêmica.

## 10. Estado Atual do Desenvolvimento

### Funcionalidades implementadas

- Backend FastAPI com SQLite, SQLModel e teste de disponibilidade em `/health`.
- Importação do catálogo a partir do CSV limpo, com capas e IDs de origem.
- Listagem paginada e consulta individual dos livros.
- Recomendação por similaridade do cosseno a partir dos embeddings exportados.
- Testes automatizados do catálogo, do importador e da recomendação.
- Interface responsiva com busca, catálogo, detalhes e recomendações integrados à API.
- API publicada no Railway com 1.795 livros e recomendações, preservados após um novo deploy.

O catálogo e as recomendações foram integrados à `main` no [PR #4](https://github.com/VitorrSan/recomendador-livros/pull/4). A integração da interface foi concluída no [PR #5](https://github.com/VitorrSan/recomendador-livros/pull/5). Os guias de execução estão nas pastas [backend](backend/README.md) e [frontend](frontend/README.md).

### Funcionalidades pendentes

- Primeira publicação da interface no GitHub Pages após a revisão do workflow.
- Avaliação da relevância do ranking e testes do fluxo completo.
- Validação da aplicação completa após a publicação da interface.

### Funcionalidades adicionais planejadas

- Busca semântica por texto.
- Perfis e autenticação de usuários.
- Registro de favoritos e interações.
- Recomendações personalizadas por interesses.
- Filtros e recursos adicionais de navegação.

## 11. Planejamento de Desenvolvimento

### Fase 1 — Infraestrutura inicial

Preparação do repositório, ambiente Python, FastAPI, SQLite e testes iniciais.

**Situação:** concluída no Backend.

### Fase 2 — Catálogo de livros

Definição do dataset, importação dos livros, consolidação dos modelos de dados e integração do catálogo com o Front-end.

O catálogo está disponível no Backend e integrado à interface.

### Fase 3 — Motor de recomendação

Os notebooks geram os embeddings. O Backend calcula o ranking de livros semelhantes com o lote validado.

### Fase 4 — Experiência principal

Construção da interface de recomendações, com destaque para a seção "Você também pode gostar" e a navegação entre livros relacionados.

A interface principal está implementada e validada localmente.

### Fase 5 — Funcionalidades complementares

Implementação da busca semântica por texto e, conforme a viabilidade, personalização por usuário.

**Situação:** planejada.

### Fase 6 — Testes, hospedagem e apresentação

Testes funcionais e de integração, avaliação das recomendações, publicação da aplicação e preparação para arguição.

**Situação:** API publicada e persistência validada. Hospedagem da interface e preparação da apresentação em andamento.

## 12. Execução Local do Backend

Com Python 3.12 instalado, coloque os [arquivos do lote](Data/README.md) nos caminhos indicados. Siga a [execução local do Backend](backend/README.md#3-preparação-do-ambiente) para instalar as dependências, validar o CSV, importar o catálogo e iniciar o servidor no PowerShell.

Depois da inicialização, abra [a documentação interativa da API](http://127.0.0.1:8000/docs) para testar o catálogo e as recomendações.

A API também está disponível na [documentação pública](https://recomendador-livros-production.up.railway.app/docs). Para usar essa API pela interface local, siga o [guia do Frontend](frontend/README.md).

## 13. Versionamento e Colaboração

O projeto utiliza Git e GitHub para organizar o desenvolvimento.

Cada integrante deverá desenvolver suas funcionalidades em branches específicas, registrar commits descritivos e utilizar Pull Requests para integração à branch principal.

O objetivo é manter um histórico de evolução claro e preservar as contribuições individuais dos integrantes.

## 14. Limitações e Considerações

O sistema é um projeto acadêmico e não pretende reproduzir integralmente os algoritmos utilizados por plataformas comerciais.

A recomendação inicial será baseada nas características semânticas dos livros.

A personalização por usuário dependerá da disponibilidade e da qualidade das interações registradas. Quando implementada, deverá considerar privacidade, controle dos dados e armazenamento seguro de informações de autenticação.

A qualidade das recomendações estará diretamente relacionada ao dataset, às descrições disponíveis e ao modelo Transformer escolhido.

O desenvolvimento priorizará uma aplicação funcional, compreensível e tecnicamente defensável, evitando complexidade desnecessária.

## 15. Contexto Acadêmico

Este projeto busca demonstrar a aplicação de Processamento de Linguagem Natural, modelos Transformers, embeddings e similaridade do cosseno em um sistema de recomendação de livros.

A proposta combina desenvolvimento web, banco de dados e Inteligência Artificial para construir uma experiência de descoberta de conteúdos baseada em similaridade semântica e, futuramente, em preferências individuais.

Além de desenvolver a aplicação, o grupo deverá compreender as decisões técnicas, os algoritmos utilizados e as limitações da solução para sua apresentação acadêmica.

## 16. Revisão de segurança antes da publicação

Na revisão de 20/11/2026, não foram encontradas credenciais nos arquivos revisados, no pacote de publicação ou no histórico Git analisado pelo Gitleaks 8.30.1. A consulta ao OSV não retornou vulnerabilidades conhecidas para as 29 versões de dependências declaradas naquele momento. Esses resultados não substituem novas verificações quando o código ou as dependências mudarem.

A inspeção também incluiu código e saídas dos notebooks, renderização de conteúdo do catálogo e os caminhos de arquivos privados na API. Os caminhos testados para `.env`, banco, Git e artefatos retornaram 404. Não há endpoints de escrita, administração ou dados de usuários no contrato atual.

Há e-mails pessoais nos metadados de autoria de alguns commits. A configuração de autoria atual e o histórico compartilhado foram mantidos. Esses e-mails não são chaves de acesso e não entram no pacote de arquivos do site.

A publicação usa uma lista explícita de cinco arquivos do frontend. Dados, banco e chaves privadas permanecem fora do GitHub e do pacote do Pages. Os scripts externos são restringidos pela CSP da interface; o workflow fixa as versões das ações por SHA e limita as permissões de publicação ao job de deploy.

A API é pública e somente de leitura. CORS restringe o acesso de páginas no navegador, mas não é autenticação nem impede consultas diretas. Controle de taxa por cliente e monitoramento de consumo são melhorias de disponibilidade para etapas futuras.
