// ===== CONFIGURAÇÃO =====
// Deixe vazio para usar os dados do arquivo dados.js (modo estático).
// Endereço do FastAPI. Ajuste este valor quando a API for publicada.
const API_URL = "http://127.0.0.1:8000";

const app = document.getElementById("app");
const campo = document.getElementById("campo");
const lista = document.getElementById("sugestoes");
const aviso = document.getElementById("aviso");   // anuncia mudanças para leitores de tela
const TITULO_SITE = document.title;

let livros = [];
let porId = {};
let homeHTML = "";
const OPCOES = "[role=option]:not([aria-disabled=true])";
let ativo = -1;        // item destacado nas sugestões (setas do teclado)
let pedido = 0;        // evita que uma resposta lenta sobrescreva uma mais nova
let navegou = false;   // true se o usuário já navegou dentro do site (para o botão Voltar)
let homeScroll = 0;    // posição da tela inicial, para voltar no mesmo ponto
if ("scrollRestoration" in history) history.scrollRestoration = "manual";

// ===== UTILITÁRIOS =====
const esc = t => String(t ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const normalizar = t => String(t ?? "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
const info = l => [l.autor, l.ano].filter(Boolean).join(", ");
const fmtNota = n => n.toFixed(2).replace(".", ",");
const reduz = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const anunciar = t => { aviso.textContent = t; };
const CORES = ["#7a2e2e", "#2f6f5e", "#1f4e79", "#8e5a2b", "#6b2d5c", "#8a6d00"];
const corDe = t => { let h = 0; for (const c of String(t)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return CORES[h % CORES.length]; };
const inteiro = x => { const n = Math.round(Number(x)); return Number.isFinite(n) && n > 0 ? n : null; };

// Aceita os nomes de colunas do dataset (title, book_cover, avg_rating...) e os nomes em português
function padronizarLivro(l, i) {
  const genero = l.genero ?? l.genre ?? l.genres ?? "";
  const capa = String(l.capa_url ?? l.capa ?? l.book_cover ?? l.cover ?? l.image_url ?? "");
  const url = String(l.url ?? "");
  return {
    id: l.id ?? l.ID ?? l.index ?? i,
    titulo: l.titulo ?? l.title ?? l.nome ?? l.name ?? "(sem título)",
    autor: l.autor ?? l.author ?? l.autores ?? l.authors ?? "",
    ano: inteiro(l.ano_publicacao ?? l.ano ?? l.year) ?? "",
    genero: Array.isArray(genero) ? (genero[0] ?? "") : genero,
    capa: /^https?:\/\//.test(capa) ? capa : "",
    nota: Number(l.nota ?? l.avg_rating ?? l.rating) || null,
    avaliacoes: inteiro(l.avaliacoes ?? l.num_ratings),
    paginas: inteiro(l.paginas ?? l.pages),
    editora: l.editora ?? l.publisher ?? "",
    descricao: l.descricao ?? l.description ?? "",
    url: /^https?:\/\//.test(url) ? url : ""
  };
}
function padronizarSimilar(s) {
  let score = Number(s.score ?? s.similaridade ?? s.similarity ?? 0);
  if (score > 1) score = score / 100;           // aceita 91 em vez de 0.91
  return { id: s.livro?.id ?? s.id ?? s.livro_id ?? s.book_id, score: Math.max(-1, Math.min(1, score || 0)) };
}

// ===== CAMADA DE DADOS (única parte que muda entre estático e API) =====
async function carregarLivros() {
  if (API_URL) {
    const catalogo = [];
    const limite = 100;
    for (let offset = 0; ; offset += limite) {
      const r = await fetch(`${API_URL}/books?offset=${offset}&limit=${limite}`);
      if (!r.ok) throw new Error(r.status);
      const pagina = await r.json();
      if (!Array.isArray(pagina)) throw new Error("Resposta de catálogo inválida");
      catalogo.push(...pagina);
      if (pagina.length < limite) return catalogo;
    }
  }
  if (typeof DADOS === "undefined") throw new Error("dados.js não carregou");
  return DADOS.livros;
}
async function buscarSimilares(id) {
  if (API_URL) {
    const r = await fetch(`${API_URL}/books/${encodeURIComponent(id)}/similar?limit=10`);
    if (!r.ok) throw new Error(r.status);
    const resultados = await r.json();
    resultados.forEach(item => {
      if (item.livro) porId[item.livro.id] = padronizarLivro(item.livro, item.livro.id);
    });
    return resultados;
  }
  return (DADOS.similares || {})[id] || [];
}

// ===== PEÇAS VISUAIS =====
const HERO = `<section class="hero"><h1>Pesquise livros usando a similaridade do cosseno</h1>
    <p>Digite o título de um livro e descubra quais outros são mais parecidos.</p></section>`;
function capaHTML(l, extra = "") {
  const img = l.capa ? `<img src="${esc(l.capa)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">` : "";
  return `<span class="capa ${extra}" style="--c:${corDe(l.titulo)}"><span class="cap-tit">${esc(l.titulo)}</span>${img}</span>`;
}
function posterHTML(l) {
  return `<button type="button" class="poster" data-id="${esc(l.id)}" aria-label="${esc(l.titulo)}${l.autor ? ", " + esc(l.autor) : ""}">
    ${capaHTML(l)}<span class="pt">${esc(l.titulo)}</span>${l.nota ? `<span class="pn">★ ${fmtNota(l.nota)}</span>` : ""}</button>`;
}
function fileiraHTML(titulo, itens) {
  return `<section class="fileira"><h2>${esc(titulo)}</h2>
    <div class="trilho-wrap"><button type="button" class="seta esq" aria-label="Anterior em ${esc(titulo)}">‹</button>
    <div class="trilho">${itens.map(posterHTML).join("")}</div>
    <button type="button" class="seta dir" aria-label="Próximos em ${esc(titulo)}">›</button></div><div class="prateleira"></div></section>`;
}
function destaqueHTML(l, porNota) {
  const meta = [l.autor, l.ano].filter(Boolean).map(esc).join(" · ");
  return `<section class="destaque" style="--c:${corDe(l.titulo)}" aria-label="Livro em destaque">${capaHTML(l, "grande")}
    <div class="dest-info"><span class="selo">${porNota ? "★ Mais bem avaliado" : "Em destaque"}</span><h2>${esc(l.titulo)}</h2>
    <p class="meta">${meta}${l.genero ? ` <span class="pill">${esc(l.genero)}</span>` : ""}</p>
    ${l.descricao ? `<p class="desc">${esc(String(l.descricao).slice(0, 240))}</p>` : ""}
    <button type="button" class="botao" data-id="${esc(l.id)}">Ver parecidos →</button></div></section>`;
}

// ===== TELA INICIAL (destaque + fileiras por categoria) =====
// "Mais bem avaliados": só entram livros com avaliações suficientes (fora os 25% com menos votos),
// para um livro com nota 5,0 e 3 votos não ficar na frente de livros avaliados por milhões de pessoas.
function ordenarPorNota() {
  const com = livros.filter(l => l.nota);
  const votos = com.map(l => l.avaliacoes || 0).sort((a, b) => a - b);
  const minimo = votos.length ? votos[Math.floor(votos.length * 0.25)] : 0;
  const cmp = (a, b) => b.nota - a.nota || (b.avaliacoes || 0) - (a.avaliacoes || 0);
  const solidos = com.filter(l => (l.avaliacoes || 0) >= minimo).sort(cmp);
  const resto = com.filter(l => (l.avaliacoes || 0) < minimo).sort(cmp);
  return { ranking: solidos, todos: [...solidos, ...resto] };
}
function montarHome() {
  const { ranking: porNota, todos } = ordenarPorNota();
  const posicao = new Map(todos.map((l, i) => [l, i]));
  const porPop = livros.filter(l => l.avaliacoes).sort((a, b) => b.avaliacoes - a.avaliacoes);
  const contagem = {};
  livros.forEach(l => { if (l.genero) contagem[l.genero] = (contagem[l.genero] || 0) + 1; });
  const generos = Object.entries(contagem).filter(([, n]) => n >= 3).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([g]) => g);

  const filas = [];
  if (porNota.length >= 3) filas.push(["Mais bem avaliados", porNota.slice(0, 20)]);
  if (porPop.length >= 3) filas.push(["Mais populares", porPop.slice(0, 20)]);
  generos.forEach(g => filas.push([g, livros.filter(l => l.genero === g)
    .sort((a, b) => (posicao.get(a) ?? 1e9) - (posicao.get(b) ?? 1e9)).slice(0, 20)]));
  if (!filas.length) filas.push(["Todos os livros", livros.slice(0, 20)]);

  homeHTML = HERO +
    destaqueHTML(porNota[0] || livros[0], porNota.length > 0) +
    filas.map(([t, l]) => fileiraHTML(t, l)).join("");
}
function mostrarHome() {
  pedido++;
  campo.value = "";
  document.title = TITULO_SITE;
  app.innerHTML = livros.length ? homeHTML
    : HERO + '<p class="vazio">Nenhum livro disponível no catálogo.</p>';
  requestAnimationFrame(() => window.scrollTo(0, navegou ? homeScroll : 0));
}

// ===== PÁGINA DE UM LIVRO (livro escolhido + parecidos com %) =====
async function mostrarLivro(id) {
  const livro = porId[id];
  const meu = ++pedido;
  campo.value = livro.titulo;
  document.title = `${livro.titulo} · Biblioteca`;
  const meta = [livro.autor, livro.ano].filter(Boolean).map(esc).join(" · ");
  const meta2 = [
    livro.nota ? `★ ${fmtNota(livro.nota)}${livro.avaliacoes ? ` (${livro.avaliacoes.toLocaleString("pt-BR")} avaliações)` : ""}` : "",
    livro.paginas ? `${livro.paginas} páginas` : "", esc(livro.editora)
  ].filter(Boolean).join(" · ");
  app.innerHTML = `<button type="button" class="voltar">← Voltar</button>
    <section class="detalhe" style="--c:${corDe(livro.titulo)}">${capaHTML(livro, "grande")}
      <div class="info"><h1>${esc(livro.titulo)}</h1>
      <p class="meta">${meta}${livro.genero ? ` <span class="pill">${esc(livro.genero)}</span>` : ""}</p>${meta2 ? `<p class="meta2">${meta2}</p>` : ""}
      ${livro.descricao ? `<p class="desc">${esc(String(livro.descricao).slice(0, 600))}</p>` : ""}
      ${livro.url ? `<p class="meta2"><a class="link" href="${esc(livro.url)}" target="_blank" rel="noopener">${/goodreads\.com/.test(livro.url) ? "Ver no Goodreads" : "Ver mais"} ↗</a></p>` : ""}</div></section>
    <div id="similares"><p class="vazio">Buscando livros parecidos...</p></div>`;
  window.scrollTo(0, 0);
  if (navegou) { const h = app.querySelector("h1"); h.tabIndex = -1; h.focus({ preventScroll: true }); } // leitor de tela começa no título
  const alvo = document.getElementById("similares");

  let similares;
  try {
    similares = (await buscarSimilares(id)).map(padronizarSimilar)
      .filter(s => porId[s.id] && String(s.id) !== String(id))
      .sort((a, b) => b.score - a.score);
  } catch (e) {
    if (meu === pedido) alvo.innerHTML = '<p class="vazio">Não foi possível buscar os livros parecidos. Verifique a conexão e tente de novo.</p>';
    return;
  }
  if (meu !== pedido) return; // chegou uma escolha mais nova enquanto esperava
  if (!similares.length) { alvo.innerHTML = '<p class="vazio">Ainda não há livros parecidos cadastrados para este livro.</p>'; return; }

  alvo.innerHTML = `<h2 class="sub">Livros mais parecidos</h2><ol>${similares.map(s => {
    const l = porId[s.id];
    const pct = Math.round(s.score * 100);
    return `<li><button type="button" class="livro" data-id="${esc(l.id)}" aria-label="${esc(l.titulo)}, ${pct}% parecido. Ver este livro">
      ${capaHTML(l, "mini")}<span class="titulo">${esc(l.titulo)}</span><span class="autor">${esc(info(l))}</span>
      <span class="anel" style="--p:${Math.max(0, pct)}" title="Similaridade do cosseno"><span class="score">${pct}%</span></span></button></li>`;
  }).join("")}</ol>`;
  anunciar(`${similares.length} livros parecidos com ${livro.titulo}`);
}

// ===== NAVEGAÇÃO (o endereço #livro-ID permite voltar e compartilhar o link) =====
function rota() {
  const m = location.hash.match(/^#livro-(.+)$/);
  let id = null;
  try { id = m ? decodeURIComponent(m[1]) : null; }
  catch { mostrarHome(); return; }
  if (id !== null && porId[id]) mostrarLivro(id);
  else mostrarHome();
}
function escolher(id) {
  fechar();
  campo.blur(); // fecha o teclado no celular
  if (app.querySelector(".hero")) homeScroll = window.scrollY;
  navegou = true;
  const novo = "#livro-" + encodeURIComponent(id);
  if (location.hash === novo) rota(); else location.hash = novo;
}
function voltar() {
  if (navegou && history.length > 1) history.back();
  else { history.pushState(null, "", location.pathname + location.search); rota(); }
}

// ===== BUSCA COM SUGESTÕES =====
function fechar() {
  lista.hidden = true;
  ativo = -1;
  campo.setAttribute("aria-expanded", "false");
  campo.removeAttribute("aria-activedescendant");
}
function marcar(i) {
  const ops = [...lista.querySelectorAll(OPCOES)];
  if (!ops.length) return;
  ativo = (i + ops.length) % ops.length;
  ops.forEach((o, k) => o.setAttribute("aria-selected", k === ativo));
  campo.setAttribute("aria-activedescendant", ops[ativo].id);
  ops[ativo].scrollIntoView({ block: "nearest" });
}
function sugerir() {
  const q = normalizar(campo.value.trim());
  lista.innerHTML = "";
  ativo = -1;
  if (!q) { fechar(); return; }
  const achados = livros
    .filter(l => l._b.includes(q))
    .sort((a, b) => b._t.startsWith(q) - a._t.startsWith(q))
    .slice(0, 6);
  if (!achados.length) {
    lista.innerHTML = '<li role="option" aria-disabled="true" class="vazio" style="padding:.6rem .8rem">Nenhum livro encontrado. Tente outro título ou autor.</li>';
  }
  achados.forEach((l, i) => {
    const li = document.createElement("li");
    li.id = "op-" + i;
    li.setAttribute("role", "option");
    li.setAttribute("aria-selected", "false");
    li.innerHTML = `${esc(l.titulo)} <small>${l.autor ? "— " + esc(l.autor) : ""}</small>`;
    li.addEventListener("mousedown", e => e.preventDefault()); // não tirar o foco do campo
    li.addEventListener("click", () => escolher(l.id));
    lista.appendChild(li);
  });
  lista.hidden = false;
  campo.setAttribute("aria-expanded", "true");
  anunciar(achados.length ? `${achados.length} sugestões` : "Nenhum livro encontrado");
}

// ===== VALIDAÇÃO (aparece no console do navegador, F12) =====
function validar() {
  if (API_URL || !livros.length) return;
  const sim = DADOS.similares || {};
  const ids = new Set(livros.map(l => String(l.id)));
  const semParecidos = livros.filter(l => !(sim[l.id] && sim[l.id].length)).length;
  let invalidos = 0;
  for (const k in sim) {
    if (!ids.has(k)) { invalidos++; continue; }
    sim[k].forEach(s => { if (!ids.has(String(s.id ?? s.livro_id ?? s.book_id))) invalidos++; });
  }
  const repetidos = livros.length - ids.size;
  if (semParecidos || invalidos || repetidos) {
    console.warn(`[dados.js] ${livros.length} livros. Sem parecidos: ${semParecidos}. Ids que não existem em "livros": ${invalidos}. Ids repetidos: ${repetidos}.`);
  } else {
    console.info(`[dados.js] ${livros.length} livros carregados, sem problemas.`);
  }
}

// ===== INÍCIO E EVENTOS =====
async function iniciar() {
  try {
    livros = (await carregarLivros()).map(padronizarLivro).filter(l => l.id !== undefined && l.id !== null);
    livros.forEach(l => { l._t = normalizar(l.titulo); l._b = l._t + " " + normalizar(l.autor); }); // busca rápida
    porId = Object.fromEntries(livros.map(l => [l.id, l]));
    if (livros.length) montarHome();
    validar();
    rota();
  } catch (e) {
    app.innerHTML = HERO + '<p class="vazio">Não foi possível carregar o catálogo. Confira a conexão e tente novamente.</p><button type="button" class="tentar">Tentar de novo</button>';
    app.querySelector(".tentar").addEventListener("click", iniciar);
  }
}

document.addEventListener("error", e => { if (e.target.tagName === "IMG") e.target.remove(); }, true); // capa quebrada: fica a lombada
window.addEventListener("hashchange", rota);
campo.addEventListener("input", sugerir);
campo.addEventListener("focus", () => { if (campo.value.trim() && lista.hidden) sugerir(); });
campo.addEventListener("keydown", e => {
  if (e.key === "ArrowDown") { e.preventDefault(); if (lista.hidden) sugerir(); marcar(ativo + 1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); marcar(ativo < 0 ? -1 : ativo - 1); }
  else if (e.key === "Escape" && !lista.hidden) { e.preventDefault(); fechar(); } // sem isso o Esc apaga o texto do campo
  else if (e.key === "Enter") {
    const op = lista.querySelectorAll(OPCOES)[ativo < 0 ? 0 : ativo];
    if (op && !lista.hidden) { e.preventDefault(); op.click(); }
  }
});
document.addEventListener("click", e => {
  if (!e.target.closest(".busca")) fechar();
  const logo = e.target.closest(".logo");
  if (logo) {
    e.preventDefault();
    homeScroll = 0;
    if (location.hash) { navegou = true; location.hash = ""; }
    else window.scrollTo({ top: 0, behavior: reduz() ? "auto" : "smooth" });
    return;
  }
  if (!app.contains(e.target)) return;
  const seta = e.target.closest(".seta");
  if (seta) {
    const t = seta.parentElement.querySelector(".trilho");
    t.scrollBy({ left: (seta.classList.contains("dir") ? 1 : -1) * t.clientWidth * 0.85, behavior: reduz() ? "auto" : "smooth" });
    return;
  }
  if (e.target.closest(".voltar")) { voltar(); return; }
  const alvo = e.target.closest("[data-id]");
  if (alvo) escolher(alvo.dataset.id);
});
iniciar();
