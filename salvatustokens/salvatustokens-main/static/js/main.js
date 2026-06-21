const nav = document.querySelector("[data-nav]");
const navToggle = document.querySelector("[data-nav-toggle]");

if (nav && navToggle) {
  navToggle.addEventListener("click", () => {
    nav.classList.toggle("is-open");
  });
}

document.querySelectorAll("[data-toc-toggle]").forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const toc = toggle.closest("[data-toc]");
    if (!toc) {
      return;
    }
    const collapsed = toc.classList.toggle("is-collapsed");
    toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
  });
});

document.querySelectorAll("[data-toc] .toc__list a").forEach((link) => {
  link.addEventListener("click", () => {
    if (window.matchMedia("(max-width: 720px)").matches) {
      const toc = link.closest("[data-toc]");
      const toggle = toc && toc.querySelector("[data-toc-toggle]");
      if (toc && toggle) {
        toc.classList.add("is-collapsed");
        toggle.setAttribute("aria-expanded", "false");
      }
    }
  });
});

const animatedItems = document.querySelectorAll("[data-animate]");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  animatedItems.forEach((item) => observer.observe(item));
} else {
  animatedItems.forEach((item) => item.classList.add("is-visible"));
}

document.querySelectorAll("[data-tilt-card]").forEach((card) => {
  card.addEventListener("pointermove", (event) => {
    const rect = card.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `rotateX(${y * -5}deg) rotateY(${x * 5}deg)`;
  });
  card.addEventListener("pointerleave", () => {
    card.style.transform = "";
  });
});

const calculator = document.querySelector("[data-calculator]");

function formatEuro(value) {
  return new Intl.NumberFormat(document.documentElement.lang === "en" ? "en-US" : "es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 2,
  }).format(value);
}

function updateCalculator() {
  if (!calculator) {
    return;
  }

  const data = new FormData(calculator);
  const inputTokens = Number(data.get("inputTokens") || 0);
  const outputTokens = Number(data.get("outputTokens") || 0);
  const inputPrice = Number(data.get("inputPrice") || 0);
  const outputPrice = Number(data.get("outputPrice") || 0);
  const localShare = Number(data.get("localShare") || 0) / 100;
  const before = (inputTokens / 1000000) * inputPrice + (outputTokens / 1000000) * outputPrice;
  const after = before * (1 - localShare);
  const savings = Math.max(0, before - after);
  const summary = document.documentElement.lang === "en"
    ? `${formatEuro(before)} before, ${formatEuro(after)} after`
    : `${formatEuro(before)} antes, ${formatEuro(after)} después`;

  calculator.querySelector("[data-local-share]").textContent = `${Math.round(localShare * 100)}%`;
  calculator.querySelector("[data-savings]").textContent = formatEuro(savings);
  calculator.querySelector("[data-before-after]").textContent = summary;
}

if (calculator) {
  calculator.addEventListener("input", updateCalculator);
  updateCalculator();
}

const tokenLab = document.querySelector("[data-token-lab]");

// Precios de referencia en USD por 1M de tokens. Se cargan desde
// /static/data/models.json (actualizado automáticamente); esto es el respaldo.
let models = [
  { name: "GPT-5.4 Pro", provider: "OpenAI", context: "256K", input: 30, output: 180,
    note: { es: "Razonamiento frontera", en: "Frontier reasoning" } },
  { name: "Claude Opus 4.7", provider: "Anthropic", context: "200K", input: 5, output: 25,
    note: { es: "Calidad premium", en: "Premium quality" } },
  { name: "GPT-5.4", provider: "OpenAI", context: "256K", input: 2.5, output: 15,
    note: { es: "Estándar potente", en: "Strong standard" } },
  { name: "Claude Sonnet 4.6", provider: "Anthropic", context: "200K", input: 3, output: 15,
    note: { es: "Equilibrado", en: "Balanced" } },
  { name: "Gemini 3.5 Flash", provider: "Google", context: "1M", input: 1.5, output: 9,
    note: { es: "Barato y rápido", en: "Cheap and fast" } },
  { name: "DeepSeek V3.2", provider: "DeepSeek", context: "128K", input: 0.28, output: 0.4,
    note: { es: "Ultra económico", en: "Ultra cheap" } },
  { name: { es: "IA local (Ollama)", en: "Local AI (Ollama)" }, provider: { es: "Local", en: "Local" },
    context: { es: "Depende", en: "It depends" }, input: 0, output: 0, local: true,
    note: { es: "Coste API cero; cuenta luz y hardware", en: "Zero API cost; consider power and hardware" } },
];

// Hardware típico con su memoria (GB) para correr modelos en local.
const hardwareTiers = [
  { group: { es: "GPU NVIDIA", en: "NVIDIA GPU" }, items: [
    { name: "RTX 4060", mem: 8 },
    { name: "RTX 4060 Ti", mem: 16 },
    { name: "RTX 4070", mem: 12 },
    { name: "RTX 4080", mem: 16 },
    { name: "RTX 4090", mem: 24 },
    { name: "RTX 5090", mem: 32 },
  ] },
  { group: { es: "GPU AMD", en: "AMD GPU" }, items: [
    { name: "RX 7600", mem: 8 },
    { name: "RX 7800 XT", mem: 16 },
    { name: "RX 7900 XTX", mem: 24 },
  ] },
  { group: { es: "Apple Silicon", en: "Apple Silicon" }, items: [
    { name: "Mac M4", mem: 16 },
    { name: "Mac M4 Pro", mem: 32 },
    { name: "Mac M4 Max", mem: 64 },
    { name: "Mac M3 Ultra", mem: 128 },
  ] },
  { group: { es: "CPU + RAM", en: "CPU + RAM" }, items: [
    { name: "Intel N100", mem: 16, cpu: true },
    { name: "PC sobremesa", mem: 32, cpu: true },
  ] },
  { group: { es: "Mini PC IA", en: "AI mini PC" }, items: [
    { name: "Ryzen AI Max+ 395", mem: 64, cpu: true },
    { name: "Ryzen AI Max+ 395", mem: 128, cpu: true },
  ] },
];

// Fecha de última actualización automática de precios (respaldo; lo pisa el JSON).
let priceUpdated = "2026-06-17";

// Conversión de moneda. Los precios por 1M se quedan en USD; el selector solo
// convierte el coste mensual a EUR con la tasa diaria del BCE (frankfurter.app).
let fxRate = 0.92;
let fxDate = null;

function currentLang() {
  return document.documentElement.lang === "en" ? "en" : "es";
}

function currentCurrency() {
  const select = tokenLab && tokenLab.querySelector("[data-currency]");
  return select && select.value === "EUR" ? "EUR" : "USD";
}

function formatMoney(usdValue) {
  if (currentCurrency() === "EUR") {
    return formatEuro(usdValue * fxRate);
  }
  return formatUsd(usdValue);
}

function localize(value) {
  if (typeof value === "string") {
    return value;
  }
  return value[currentLang()] || value.es;
}

function formatNumber(value) {
  return new Intl.NumberFormat(document.documentElement.lang === "en" ? "en-US" : "es-ES").format(value);
}

function formatUsd(value) {
  return new Intl.NumberFormat(document.documentElement.lang === "en" ? "en-US" : "es-ES", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value < 1 ? 4 : 2,
  }).format(value);
}

function estimateTokens(text) {
  const trimmed = text.trim();
  const chars = trimmed.length;
  const charsNoSpaces = trimmed.replace(/\s/g, "").length;
  const words = trimmed ? (trimmed.match(/[\p{L}\p{N}_-]+/gu) || []).length : 0;
  const cjkChars = (trimmed.match(/[\u3040-\u30ff\u3400-\u9fff]/g) || []).length;
  const punctuation = (trimmed.match(/[{}[\]():;,."'/\\|=+\-*<>#`]/g) || []).length;
  const lines = trimmed ? trimmed.split(/\n/).length : 0;
  let type = document.documentElement.lang === "en" ? "Text" : "Texto";
  let ratio = 1.45;

  try {
    if (trimmed && JSON.parse(trimmed)) {
      type = "JSON";
      ratio = 3.2;
    }
  } catch (error) {
    const codeHints = /(function|const|let|def |class |import |SELECT |curl |=>|<\/?[a-z])/i.test(trimmed);
    if (codeHints || punctuation > words * 0.7) {
      type = document.documentElement.lang === "en" ? "Code / technical" : "Código / técnico";
      ratio = 2.45;
    }
  }

  let tokens = Math.ceil(words * ratio + punctuation * 0.35 + lines * 0.6);
  if (cjkChars > chars * 0.25) {
    type = "CJK";
    tokens = Math.ceil(cjkChars * 1.8 + (chars - cjkChars) / 4);
  }
  if (!trimmed) {
    tokens = 0;
  }

  return { tokens, words, chars, charsNoSpaces, type };
}

function rowMonthly(inputPrice, outputPrice, inputTokens, outputTokens, requests, cacheRate) {
  const cachedInput = inputTokens * cacheRate;
  const normalInput = inputTokens - cachedInput;
  const perRequest = (normalInput / 1000000) * inputPrice
    + (cachedInput / 1000000) * (inputPrice * 0.1)
    + (outputTokens / 1000000) * outputPrice;
  return perRequest * requests;
}

function renderModelTable() {
  if (!tokenLab) {
    return;
  }
  const tbody = tokenLab.querySelector("[data-model-table]");
  tbody.innerHTML = models.map((model, i) => {
    const priceCells = model.local
      ? `<td class="num">${formatUsd(0)}</td><td class="num">${formatUsd(0)}</td>`
      : `<td class="num"><input class="price-input" type="number" min="0" step="0.01" inputmode="decimal" aria-label="${localize(model.name)} input" data-row="${i}" data-row-field="input" value="${model.input}"></td>`
        + `<td class="num"><input class="price-input" type="number" min="0" step="0.01" inputmode="decimal" aria-label="${localize(model.name)} output" data-row="${i}" data-row-field="output" value="${model.output}"></td>`;
    return `<tr${model.local ? ' class="row-local"' : ""}>`
      + `<td><strong>${localize(model.name)}</strong><small>${localize(model.note)}</small></td>`
      + `<td>${localize(model.provider)}</td>`
      + `<td>${localize(model.context)}</td>`
      + priceCells
      + `<td class="num"><strong data-monthly="${i}">—</strong></td>`
      + `</tr>`;
  }).join("");
}

function updateModelCosts(metrics) {
  const expectedOutput = Number(tokenLab.querySelector("[data-expected-output]").value || 0);
  const requests = Number(tokenLab.querySelector("[data-requests-month]").value || 0);
  const cacheRate = Number(tokenLab.querySelector("[data-cache-rate]").value || 0) / 100;

  models.forEach((model, i) => {
    let inputPrice = model.input;
    let outputPrice = model.output;
    if (!model.local) {
      const fieldIn = tokenLab.querySelector(`[data-row="${i}"][data-row-field="input"]`);
      const fieldOut = tokenLab.querySelector(`[data-row="${i}"][data-row-field="output"]`);
      inputPrice = Number((fieldIn && fieldIn.value) || 0);
      outputPrice = Number((fieldOut && fieldOut.value) || 0);
    }
    const monthly = rowMonthly(inputPrice, outputPrice, metrics.tokens, expectedOutput, requests, cacheRate);
    const cell = tokenLab.querySelector(`[data-monthly="${i}"]`);
    if (cell) {
      cell.textContent = formatMoney(monthly);
    }
  });
}

function updatePriceDate() {
  if (!tokenLab) {
    return;
  }
  const el = tokenLab.querySelector("[data-price-updated]");
  if (!el || !priceUpdated) {
    return;
  }
  const parsed = new Date(`${priceUpdated}T00:00:00`);
  el.textContent = Number.isNaN(parsed.getTime())
    ? priceUpdated
    : parsed.toLocaleDateString(currentLang() === "en" ? "en-US" : "es-ES", {
        day: "numeric", month: "long", year: "numeric",
      });
}

function setFxLabel() {
  if (!tokenLab) {
    return;
  }
  const note = tokenLab.querySelector("[data-fx-note]");
  if (!note) {
    return;
  }
  if (currentCurrency() !== "EUR") {
    note.hidden = true;
    note.textContent = "";
    return;
  }
  const rate = new Intl.NumberFormat(currentLang() === "en" ? "en-US" : "es-ES", {
    minimumFractionDigits: 2, maximumFractionDigits: 4,
  }).format(fxRate);
  let when = "";
  if (fxDate) {
    const parsed = new Date(`${fxDate}T00:00:00`);
    if (!Number.isNaN(parsed.getTime())) {
      when = ` · ${currentLang() === "en" ? "ECB" : "BCE"} ${parsed.toLocaleDateString(
        currentLang() === "en" ? "en-US" : "es-ES", { day: "numeric", month: "short" })}`;
    }
  }
  note.hidden = false;
  note.textContent = `1 USD ≈ ${rate} €${when}`;
}

async function loadModelData() {
  if (!tokenLab) {
    return;
  }
  try {
    const res = await fetch("/static/data/models.json", { cache: "no-cache" });
    if (!res.ok) {
      return;
    }
    const data = await res.json();
    if (Array.isArray(data.models) && data.models.length) {
      models = data.models;
      if (data.updated) {
        priceUpdated = data.updated;
      }
      renderModelTable();
      updateTokenLab();
      updatePriceDate();
    }
  } catch (error) {
    // Sin red o JSON inválido: nos quedamos con el respaldo embebido.
  }
}

async function initCurrency() {
  try {
    const cached = JSON.parse(localStorage.getItem("fxUsdEur") || "null");
    if (cached && cached.rate) {
      fxRate = cached.rate;
      fxDate = cached.date || null;
    }
  } catch (error) {
    // localStorage no disponible: usamos el respaldo.
  }
  setFxLabel();
  try {
    const res = await fetch("https://api.frankfurter.app/latest?from=USD&to=EUR");
    if (!res.ok) {
      return;
    }
    const data = await res.json();
    if (data && data.rates && data.rates.EUR) {
      fxRate = data.rates.EUR;
      fxDate = data.date || null;
      try {
        localStorage.setItem("fxUsdEur", JSON.stringify({ rate: fxRate, date: fxDate }));
      } catch (error) {
        // Ignoramos fallos de almacenamiento.
      }
      setFxLabel();
      if (currentCurrency() === "EUR") {
        updateTokenLab();
      }
    }
  } catch (error) {
    // Sin red: mantenemos la tasa de respaldo.
  }
}

function updateTokenLab() {
  if (!tokenLab) {
    return;
  }

  const text = tokenLab.querySelector("[data-token-text]").value;
  const metrics = estimateTokens(text);
  const cacheRate = Number(tokenLab.querySelector("[data-cache-rate]").value || 0) / 100;

  tokenLab.querySelector('[data-metric="tokens"]').textContent = formatNumber(metrics.tokens);
  tokenLab.querySelector('[data-metric="words"]').textContent = formatNumber(metrics.words);
  tokenLab.querySelector('[data-metric="chars"]').textContent = formatNumber(metrics.chars);
  tokenLab.querySelector('[data-metric="type"]').textContent = metrics.type;
  tokenLab.querySelector("[data-cache-output]").textContent = `${Math.round(cacheRate * 100)}%`;

  setFxLabel();
  updateModelCosts(metrics);
}

function updateFlowLab() {
  if (!tokenLab) {
    return;
  }

  const inputTokens = Number(tokenLab.querySelector("[data-flow-input]").value || 0);
  const outputTokens = Number(tokenLab.querySelector("[data-flow-output]").value || 0);
  const inputPrice = Number(tokenLab.querySelector("[data-flow-input-price]").value || 0);
  const outputPrice = Number(tokenLab.querySelector("[data-flow-output-price]").value || 0);
  const reduction = Number(tokenLab.querySelector("[data-flow-reduction]").value || 0) / 100;
  const local = Number(tokenLab.querySelector("[data-flow-local]").value || 0) / 100;

  const before = (inputTokens / 1000000) * inputPrice + (outputTokens / 1000000) * outputPrice;
  const reducedInput = inputTokens * (1 - reduction);
  const paidShare = 1 - local;
  const after = ((reducedInput * paidShare) / 1000000) * inputPrice
    + ((outputTokens * paidShare) / 1000000) * outputPrice;
  const saving = Math.max(0, before - after);
  const savingRate = before ? saving / before : 0;
  const advice = document.documentElement.lang === "en"
    ? `You would spend ${Math.round(savingRate * 100)}% less. Start by validating the local route with 30 real examples.`
    : `Gastarías un ${Math.round(savingRate * 100)}% menos. Empieza validando la ruta local con 30 ejemplos reales.`;

  tokenLab.querySelector("[data-flow-reduction-output]").textContent = `${Math.round(reduction * 100)}%`;
  tokenLab.querySelector("[data-flow-local-output]").textContent = `${Math.round(local * 100)}%`;
  tokenLab.querySelector("[data-flow-before]").textContent = formatEuro(before);
  tokenLab.querySelector("[data-flow-after]").textContent = formatEuro(after);
  tokenLab.querySelector("[data-flow-saving]").textContent = formatEuro(saving);
  tokenLab.querySelector("[data-flow-advice]").textContent = advice;
}

function updateLocalLab() {
  if (!tokenLab) {
    return;
  }

  const size = Number(tokenLab.querySelector("[data-model-size]").value || 0);
  const bytesPerParam = Number(tokenLab.querySelector("[data-quantization]").value || 0.5);
  const outputTokens = Number(tokenLab.querySelector("[data-speed-tokens]").value || 0);
  const speed = Math.max(1, Number(tokenLab.querySelector("[data-speed-rate]").value || 1));
  const rawGb = size * bytesPerParam;
  const bufferGb = rawGb * 1.28 + 1.2;
  const seconds = outputTokens / speed;
  const advice = document.documentElement.lang === "en"
    ? "Use this as a first-pass estimate. Real memory also depends on context length, KV cache, runtime and batch size."
    : "Úsalo como primera estimación. La memoria real también depende del contexto, KV cache, runtime y tamaño de lote.";

  tokenLab.querySelector("[data-ram-result]").textContent = `${rawGb.toFixed(1)} GB`;
  tokenLab.querySelector("[data-ram-buffer]").textContent = `${bufferGb.toFixed(1)} GB`;
  tokenLab.querySelector("[data-speed-result]").textContent = `${seconds.toFixed(seconds > 10 ? 0 : 1)} s`;
  tokenLab.querySelector("[data-local-advice]").textContent = advice;

  renderHardware(bufferGb);
}

function renderHardware(neededGb) {
  const container = tokenLab.querySelector("[data-hardware-list]");
  if (!container) {
    return;
  }
  const cpuTag = currentLang() === "en" ? "CPU only" : "solo CPU";
  container.innerHTML = hardwareTiers.map((tier) => {
    const chips = tier.items.map((item) => {
      const fits = neededGb <= item.mem;
      const tag = item.cpu ? `<span class="hw-cpu">${cpuTag}</span>` : "";
      return `<span class="hw-chip ${fits ? "is-fit" : "is-tight"}">`
        + `<span class="hw-mark" aria-hidden="true">${fits ? "✓" : "✗"}</span>`
        + `<span class="hw-name">${item.name}</span>`
        + `<span class="hw-mem">${item.mem} GB</span>${tag}`
        + `</span>`;
    }).join("");
    return `<div class="hardware-group"><span class="hw-group-label">${localize(tier.group)}</span><div class="hw-chips">${chips}</div></div>`;
  }).join("");
}

if (tokenLab) {
  tokenLab.querySelectorAll("[data-tab-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.dataset.tabButton;
      tokenLab.querySelectorAll("[data-tab-button]").forEach((item) => {
        item.classList.toggle("is-active", item === button);
        item.setAttribute("aria-selected", item === button ? "true" : "false");
      });
      tokenLab.querySelectorAll("[data-tab-panel]").forEach((panel) => {
        panel.classList.toggle("is-active", panel.dataset.tabPanel === tab);
      });
    });
  });

  tokenLab.addEventListener("input", () => {
    updateTokenLab();
    updateFlowLab();
    updateLocalLab();
  });

  tokenLab.querySelector("[data-clear-text]").addEventListener("click", () => {
    tokenLab.querySelector("[data-token-text]").value = "";
    updateTokenLab();
  });

  tokenLab.querySelectorAll("[data-sample]").forEach((button) => {
    button.addEventListener("click", () => {
      const samples = {
        es: {
          json: '{"objetivo":"resumir tickets","datos":[{"tipo":"vpn","prioridad":"media"},{"tipo":"correo","prioridad":"alta"}],"restricciones":["responder en JSON","no inventar campos"]}',
          prompt: 'Objetivo: resumir una conversación de soporte técnico. Datos relevantes: el usuario no puede entrar por VPN, ya reinició el router y el error aparece después de introducir MFA. Restricciones: devuelve pasos concretos, separa diagnóstico de solución y no propongas reinstalar todo.',
        },
        en: {
          json: '{"goal":"summarize tickets","data":[{"type":"vpn","priority":"medium"},{"type":"email","priority":"high"}],"constraints":["answer in JSON","do not invent fields"]}',
          prompt: 'Goal: summarize a technical support conversation. Relevant data: the user cannot connect to VPN, already restarted the router and the error appears after MFA. Constraints: return concrete steps, separate diagnosis from solution and do not suggest reinstalling everything.',
        },
      };
      const sample = button.dataset.sample === "json"
        ? samples[currentLang()].json
        : samples[currentLang()].prompt;
      tokenLab.querySelector("[data-token-text]").value = sample;
      updateTokenLab();
    });
  });

  renderModelTable();
  updateTokenLab();
  updatePriceDate();
  updateFlowLab();
  updateLocalLab();
  loadModelData();
  initCurrency();
}

document.querySelectorAll("[data-neural-canvas]").forEach((canvas) => {
  const ctx = canvas.getContext("2d");
  const nodes = [];
  let width = 0;
  let height = 0;
  let frame = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    width = Math.max(1, Math.floor(rect.width * devicePixelRatio));
    height = Math.max(1, Math.floor(rect.height * devicePixelRatio));
    canvas.width = width;
    canvas.height = height;
    nodes.length = 0;
    const count = Math.min(54, Math.max(22, Math.floor(rect.width / 28)));
    for (let i = 0; i < count; i += 1) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.22 * devicePixelRatio,
        vy: (Math.random() - 0.5) * 0.22 * devicePixelRatio,
        r: (1.4 + Math.random() * 1.6) * devicePixelRatio,
      });
    }
  }

  function draw() {
    frame = requestAnimationFrame(draw);
    ctx.clearRect(0, 0, width, height);
    ctx.lineWidth = devicePixelRatio;

    nodes.forEach((node) => {
      node.x += node.vx;
      node.y += node.vy;
      if (node.x < 0 || node.x > width) node.vx *= -1;
      if (node.y < 0 || node.y > height) node.vy *= -1;
    });

    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const max = 150 * devicePixelRatio;
        if (dist < max) {
          ctx.strokeStyle = `rgba(31, 111, 169, ${0.16 * (1 - dist / max)})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    nodes.forEach((node, index) => {
      ctx.fillStyle = index % 5 === 0 ? "rgba(244, 184, 0, 0.5)" : "rgba(79, 163, 227, 0.45)";
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  const motionAllowed = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  resize();
  window.addEventListener("resize", resize);
  if (motionAllowed) {
    draw();
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(frame);
    } else if (motionAllowed) {
      draw();
    }
  });
});
