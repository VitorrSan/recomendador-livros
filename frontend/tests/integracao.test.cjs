const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const codigo = fs
  .readFileSync(path.join(__dirname, "..", "script.js"), "utf8")
  .replace(/\biniciar\(\);\s*$/, "");

function carregarInterface(fetch, configuracao) {
  const elementos = Object.fromEntries(
    ["app", "campo", "sugestoes", "aviso"].map(id => [
      id,
      { innerHTML: "", value: "", addEventListener() {} },
    ]),
  );
  const contexto = vm.createContext({
    document: {
      title: "Biblioteca",
      getElementById: id => elementos[id],
      addEventListener() {},
    },
    window: { addEventListener() {}, scrollTo() {} },
    history: {},
    location: { hash: "" },
    requestAnimationFrame: callback => callback(),
    fetch,
    CONFIGURACAO: configuracao,
  });
  vm.runInContext(
    codigo + "\nglobalThis.livroRegistrado = id => porId[id];",
    contexto,
    { filename: "script.js" },
  );
  return { contexto, elementos };
}

test("carrega todas as páginas do catálogo pela rota do Backend", async () => {
  const livros = Array.from({ length: 205 }, (_, indice) => ({
    id: indice + 1,
    titulo: "Livro " + (indice + 1),
  }));
  const chamadas = [];
  const { contexto } = carregarInterface(async endereco => {
    const url = new URL(endereco);
    assert.equal(url.pathname, "/books");
    const offset = Number(url.searchParams.get("offset"));
    const limit = Number(url.searchParams.get("limit"));
    chamadas.push({ offset, limit });
    return { ok: true, json: async () => livros.slice(offset, offset + limit) };
  });

  const catalogo = await contexto.carregarLivros();

  assert.deepEqual(Array.from(catalogo, livro => livro.id), livros.map(livro => livro.id));
  assert.deepEqual(chamadas, [
    { offset: 0, limit: 100 },
    { offset: 100, limit: 100 },
    { offset: 200, limit: 100 },
  ]);
});

test("preserva capa e ano retornados pelo Backend e aceita dados estáticos", () => {
  const { contexto } = carregarInterface();
  const livro = contexto.padronizarLivro({
    id: 61,
    titulo: "Uma viagem",
    ano_publicacao: 2024,
    capa_url: "https://covers.example.org/61.jpg",
  });

  assert.equal(livro.id, 61);
  assert.equal(livro.ano, 2024);
  assert.equal(livro.capa, "https://covers.example.org/61.jpg");

  const estatico = contexto.padronizarLivro({
    id: 7,
    title: "Another journey",
    year: 2020,
    book_cover: "https://covers.example.org/7.jpg",
  });
  assert.equal(estatico.titulo, "Another journey");
  assert.equal(estatico.ano, 2020);
  assert.equal(estatico.capa, "https://covers.example.org/7.jpg");
});

test("interpreta a recomendação com livro aninhado e cosseno negativo", () => {
  const { contexto } = carregarInterface();
  const recomendacao = contexto.padronizarSimilar({
    livro: { id: 1326 },
    similaridade: -0.25,
  });

  assert.equal(recomendacao.id, 1326);
  assert.equal(recomendacao.score, -0.25);
  assert.equal(contexto.padronizarSimilar({ id: 7, score: 0.8 }).score, 0.8);
});

test("consulta similares e registra os livros retornados para navegação", async () => {
  const livro = {
    id: 1326,
    titulo: "Somewhere Beyond the Sea",
    ano_publicacao: 2024,
    capa_url: "https://covers.example.org/1326.jpg",
  };
  const resultados = [{ livro, similaridade: 0.834961 }];
  const chamadas = [];
  const { contexto } = carregarInterface(async endereco => {
    chamadas.push(endereco);
    return { ok: true, json: async () => resultados };
  });

  const resposta = await contexto.buscarSimilares(1);

  assert.deepEqual(chamadas, ["http://127.0.0.1:8000/books/1/similar?limit=10"]);
  assert.equal(resposta, resultados);
  const registrado = contexto.livroRegistrado(1326);
  assert.equal(registrado.titulo, livro.titulo);
  assert.equal(registrado.capa, livro.capa_url);
  assert.equal(registrado.ano, livro.ano_publicacao);
});

test("hash malformado abre a tela inicial sem erro de URI", () => {
  const { contexto, elementos } = carregarInterface();
  contexto.location.hash = "#livro-%";

  assert.doesNotThrow(() => contexto.rota());
  assert.match(elementos.app.innerHTML, /class="hero"/);
});

test("usa a API configurada sem duplicar a barra do endereço", async () => {
  const chamadas = [];
  const { contexto } = carregarInterface(async endereco => {
    chamadas.push(endereco);
    return { ok: true, json: async () => [] };
  }, { API_URL: " https://api.example.org/ " });

  await contexto.carregarLivros();
  await contexto.buscarSimilares(1);

  assert.deepEqual(chamadas, [
    "https://api.example.org/books?offset=0&limit=100",
    "https://api.example.org/books/1/similar?limit=10",
  ]);
});

test("nomes herdados de Object não são tratados como IDs de livros", () => {
  const { contexto, elementos } = carregarInterface();
  vm.runInContext("porId = Object.fromEntries([])", contexto);

  for (const id of ["constructor", "__proto__", "toString"]) {
    contexto.location.hash = "#livro-" + id;
    contexto.rota();
    assert.match(elementos.app.innerHTML, /class="hero"/);
  }
});

test("API_URL vazia mantém o modo estático sem fazer consultas HTTP", async () => {
  const { contexto } = carregarInterface(() => {
    assert.fail("O modo estático não deve consultar a API");
  }, { API_URL: "" });
  const dados = { livros: [{ id: 1, titulo: "Livro local" }], similares: { 1: [] } };
  contexto.DADOS = dados;

  assert.equal(await contexto.carregarLivros(), dados.livros);
  assert.equal(await contexto.buscarSimilares(1), dados.similares[1]);
});
