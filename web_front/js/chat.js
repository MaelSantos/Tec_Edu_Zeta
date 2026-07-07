let currentMode = 'RESUMO';
let lastResponseData = null;
var debugHistory = [];
var isProcessing = false;

function selectMode(mode, btn) {
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
}

function now() {
  return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function appendMsg(text, sender) {
  const area = document.getElementById('chat-history');
  const div = document.createElement('div');
  div.className = 'msg ' + sender;
  const inner = document.createElement('div');
  const bubble = document.createElement('div');
  bubble.className = 'bubble-msg';
  bubble.innerHTML = text;
  const time = document.createElement('div');
  time.className = 'msg-time';
  time.textContent = now();
  inner.appendChild(bubble);
  inner.appendChild(time);
  div.appendChild(inner);
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
  return bubble;
}

function showTyping() {
  const area = document.getElementById('chat-history');
  const div = document.createElement('div');
  div.className = 'msg bot';
  div.id = 'typing-indicator';
  div.innerHTML = '<div><div class="bubble-msg typing">Pensando&nbsp;<span></span><span></span><span></span></div></div>';
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById('typing-indicator');
  if (t) t.remove();
}

function getModeLabel(mode) {
  const labels = { RESUMO: 'Resumo', EXERCICIO: 'Exerc\u00edcio', REVISAO: 'Revis\u00e3o', QUIZ: 'Quiz' };
  return labels[mode] || 'Resumo';
}

function toggleDebugPanel() {
  const panel = document.getElementById('debug-panel');
  if (!panel) return;
  panel.classList.toggle('collapsed');
  if (!panel.classList.contains('collapsed')) {
    renderDebugHistory();
  }
}

function toggleDebugContent() {
  // No-op: content always shown now, collapse is handled by panel toggle
}

function escJson(str) {
  if (str == null) return '';
  const d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

function toolShortName(name) {
  if (!name) return '---';
  var m = name.match(/(\w+)Tools?\.(\w+)/);
  if (m) return m[1] + '.' + m[2];
  var labels = {
    'web_search': 'DuckDuckGo',
    'valyu_search': 'Valyu',
    'search_news': 'DuckDuckGo (news)',
  };
  return labels[name] || name;
}

function renderSingleDebugOp(op, hasNext) {
  var icons = {
    'usuario': '\u{1F4AC}',
    'ferramenta': '\u{1F50D}',
    'resultado': '\u{1F4E5}',
    'resposta': '\u{1F4CA}',
    'tentativas': '\u{1F504}',
    'modo': '\u{1F3AD}',
    'info': '\u{2139}',
    'conteudo': '\u{1F4DD}',
    'bloqueio': '\u{26D4}',
    'sem_ferramentas': '\u{1F6AB}',
    'classificador': '\u{1F9E9}',
    'busca': '\u{1F50D}',
    'resultados': '\u{1F4CA}',
    'formatacao': '\u{270D}\u{FE0F}',
  };
  var t = op.tipo || op.type || '';
  var icon = icons[t] || '\u2699';

  var h = '<div class="flow-node ' + escJson(t) + '">';
  h += '<div class="flow-node-line"><div class="flow-node-dot">' + icon + '</div>';
  if (hasNext) h += '<div class="flow-node-connector"></div>';
  h += '</div>';
  h += '<div class="flow-node-body">';

  if (t === 'usuario') {
    h += '<div class="flow-node-title">PERGUNTA</div>';
    var c = op.conteudo || op.content || '';
    if (c) {
      h += '<div class="flow-node-detail">' + escJson(c) + '</div>';
    }
  } else if (t === 'ferramenta') {
    var tn = toolShortName(op.nome || op.name || '');
    h += '<div class="flow-node-title">FERRAMENTA: ' + escJson(tn) + '</div>';
    var q = op.consulta || op.query || '';
    if (q) {
      if (typeof q !== 'string') q = JSON.stringify(q);
      h += '<div class="flow-node-meta">Consulta: ' + escJson(q) + '</div>';
    }
    if (op.duracao_seg != null) {
      h += '<div class="flow-node-meta">Dura\u00e7\u00e3o: ' + escJson(op.duracao_seg) + 's</div>';
    }
  } else if (t === 'resultado') {
    var tn = toolShortName(op.ferramenta || '');
    var status = op.status || '';
    var statusClass = '';
    var statusLabel = '';
    if (status === 'sem_resultados') {
      statusClass = ' status-nodata';
      statusLabel = ' (sem resultados)';
    } else if (status === 'bloqueado') {
      statusClass = ' status-block';
      statusLabel = ' (bloqueado)';
    }
    h += '<div class="flow-node-title' + statusClass + '">RESULTADO (' + escJson(tn) + ')' + statusLabel + '</div>';
    if (op.sites && op.sites.length > 0) {
      h += '<div class="flow-node-meta">Sites: <span style="font-size:11px;">' + op.sites.map(function(s) { return '<a href="' + escJson(s) + '" target="_blank" style="color:#8AAAC8;text-decoration:underline;">' + escJson(s.replace(/^https?:\/\//, '').slice(0, 40)) + '</a>'; }).join(' | ') + '</span></div>';
    }
    var p = op.previa || op.preview || '';
    if (p) {
      h += '<div class="flow-node-detail">' + escJson(p) + '</div>';
    }
  } else if (t === 'resposta') {
    var st = op.status || '';
    var sc = '';
    var titleClass = '';
    if (st === 'bloqueio') { sc = ' status-block'; titleClass = ' status-block'; }
    else if (st === 'sem_resultados') { sc = ' status-nodata'; }
    if (st === 'bloqueio') {
      h += '<div class="flow-node-title' + titleClass + '">CONTE\u00daDO BLOQUEADO</div>';
    } else if (st === 'sem_resultados') {
      h += '<div class="flow-node-title' + titleClass + '">SEM RESULTADOS</div>';
    } else {
      h += '<div class="flow-node-title' + titleClass + '">DADOS COLETADOS</div>';
    }
    if (op.duracao_seg != null) {
      h += '<div class="flow-node-meta">Dura\u00e7\u00e3o: ' + escJson(op.duracao_seg) + 's</div>';
    }
    var p = op.previa || op.preview || '';
    if (p) {
      h += '<div class="flow-node-detail' + sc + '">' + escJson(p) + '</div>';
    }
  } else if (t === 'tentativas') {
    h += '<div class="flow-node-title">TENTATIVAS</div>';
    if (op.tentativas && op.tentativas.length > 0) {
      for (var k = 0; k < op.tentativas.length; k++) {
        var ta = op.tentativas[k];
        var cor = ta.status === 'sucesso' ? '#2E7D32' : (ta.status === 'timeout' ? '#C62828' : '#E65100');
        h += '<div class="flow-node-meta" style="color:' + cor + ';">#' + escJson(ta.tentativa) + ' ' + escJson(ta.status) + (ta.fase ? ' (' + escJson(ta.fase) + ')' : '') + (ta.tempo_seg != null ? ' - ' + escJson(ta.tempo_seg) + 's' : '') + (ta.erro ? ' - ' + escJson(ta.erro) : '') + '</div>';
      }
    }
  } else if (t === 'modo') {
    h += '<div class="flow-node-title">FORMATA\u00c7\u00c3O: ' + escJson(op.modo || '') + '</div>';
  } else if (t === 'sem_ferramentas') {
    h += '<div class="flow-node-title">NENHUMA FERRAMENTA</div>';
    var c2 = op.conteudo || '';
    if (c2) {
      h += '<div class="flow-node-meta" style="color:#E65100;">' + escJson(c2) + '</div>';
    }
  } else if (t === 'classificador') {
    h += '<div class="flow-node-title">CLASSIFICADOR</div>';
    h += '<div class="flow-node-meta">Resultado: ' + escJson(op.resultado || '') + '</div>';
    if (op.conteudo) {
      h += '<div class="flow-node-detail">' + escJson(op.conteudo) + '</div>';
    }
  } else if (t === 'busca') {
    h += '<div class="flow-node-title">BUSCA NA WEB</div>';
    var q = op.consulta || op.query || op.previa || '';
    if (q) {
      h += '<div class="flow-node-meta">Consulta: ' + escJson(q) + '</div>';
    }
    var src = op.fonte || '';
    if (src) {
      h += '<div class="flow-node-meta">Fonte: ' + escJson(src) + '</div>';
    }
    if (op.duracao_seg != null) {
      h += '<div class="flow-node-meta">Dura\u00e7\u00e3o: ' + escJson(op.duracao_seg) + 's</div>';
    }
  } else if (t === 'resultados') {
    h += '<div class="flow-node-title">RESULTADOS DA BUSCA</div>';
    if (op.total != null) {
      h += '<div class="flow-node-meta">Total: ' + escJson(op.total) + ' resultados</div>';
    }
    if (op.sites && op.sites.length > 0) {
      h += '<div class="flow-node-meta">Fontes: <span style="font-size:11px;">' + op.sites.map(function(s) { return '<a href="' + escJson(s) + '" target="_blank" style="color:#8AAAC8;text-decoration:underline;">' + escJson(s.replace(/^https?:\/\//, '').slice(0, 40)) + '</a>'; }).join(' | ') + '</span></div>';
    }
    var p = op.previa || op.preview || '';
    if (p) {
      h += '<div class="flow-node-detail">' + escJson(p) + '</div>';
    }
  } else if (t === 'formatacao') {
    h += '<div class="flow-node-title">FORMATA\u00c7\u00c3O</div>';
    if (op.modo) {
      h += '<div class="flow-node-meta">Modo: ' + escJson(op.modo) + '</div>';
    }
  } else if (t === 'info' || t === 'conteudo' || t === 'bloqueio') {
    var label = t === 'info' ? 'INFORMA\u00c7\u00c3O' : (t === 'bloqueio' ? 'BLOQUEADO' : 'CONTE\u00daDO');
    var blockClass = t === 'bloqueio' ? ' status-block' : '';
    h += '<div class="flow-node-title' + blockClass + '">' + label + '</div>';
    var c2 = op.conteudo || op.previa || op.preview || '';
    if (c2) {
      h += '<div class="flow-node-detail' + blockClass + '">' + escJson(c2) + '</div>';
    }
  } else {
    h += '<div class="flow-node-title">' + escJson(t.toUpperCase()) + '</div>';
    var p = op.previa || op.preview || '';
    if (p) {
      h += '<div class="flow-node-detail">' + escJson(p) + '</div>';
    }
  }
  h += '</div></div>';
  return h;
}

function renderDebugHistory() {
  const container = document.getElementById('debug-ops');
  const pre = document.getElementById('debug-json');
  if (!container) return;
  if (debugHistory.length === 0) {
    container.style.display = 'block';
    if (pre) pre.style.display = 'none';
    container.innerHTML = '<div style="color:#8AAAC8;padding:12px;text-align:center;font-size:12px;">Nenhuma opera\u00e7\u00e3o do agente.</div>';
    return;
  }
  container.style.display = 'block';
  if (pre) pre.style.display = 'none';
  var html = '';
  for (var m = 0; m < debugHistory.length; m++) {
    var entry = debugHistory[m];
    var label = entry.label || 'FALHA NA OPERA\u00c7\u00c3O';
    var collapsedId = 'debug-collapse-' + m;
    var isNewest = (m === debugHistory.length - 1);
    var ops = entry.ops || [];
    var hasBlock = ops.some(function(o) { return o.tipo === 'bloqueio'; });
    html += '<div class="debug-log-entry' + (hasBlock ? ' blocked' : '') + '">';
    html += '<div class="debug-log-header" onclick="toggleDebugLog(\'' + collapsedId + '\')">';
    html += '<span class="debug-log-toggle">' + (isNewest ? '\u25BC' : '\u25B6') + '</span>';
    html += '<span class="debug-log-title">' + escJson(label.toUpperCase ? label.toUpperCase() : label) + '</span>';
    html += '</div>';
    html += '<div id="' + collapsedId + '" class="debug-log-body' + (isNewest ? '' : ' collapsed') + '">';
    html += '<div class="flow-chart">';
    for (var i = 0; i < ops.length; i++) {
      html += renderSingleDebugOp(ops[i], i < ops.length - 1);
    }
    html += '</div></div></div>';
  }
  container.innerHTML = html;
}

function toggleDebugLog(id) {
  var body = document.getElementById(id);
  if (!body) return;
  var header = body.previousElementSibling;
  body.classList.toggle('collapsed');
  if (header) {
    var toggle = header.querySelector('.debug-log-toggle');
    if (toggle) toggle.textContent = body.classList.contains('collapsed') ? '\u25B6' : '\u25BC';
  }
}

function updateDebugContent(data) {
  if (!data) return;
  // Append to debug history
  if (data._debug && Array.isArray(data._debug) && data._debug.length > 0) {
    // Use student's question as title, prefixed by mode
    var title = null;
    var modo = '';
    var isBlocked = false;
    var hasUsuario = false;
    for (var d = 0; d < data._debug.length; d++) {
      var item = data._debug[d];
      if (item.tipo === 'modo' && item.modo) {
        modo = item.modo.toUpperCase();
      }
      if (item.tipo === 'usuario' && item.conteudo) {
        hasUsuario = true;
        title = item.conteudo;
        if (title.length > 50) title = title.slice(0, 47) + '...';
      }
      if (item.tipo === 'bloqueio') {
        isBlocked = true;
      }
    }
    if (!hasUsuario) {
      if (isBlocked) {
        title = 'BLOQUEADO';
      } else if (modo) {
        title = modo;
        modo = '';
      } else {
        title = 'FALHA NA OPERA\u00c7\u00c3O';
      }
    }
    var label = modo ? modo + ': ' + title.toUpperCase() : title.toUpperCase();
    debugHistory.push({ label: label, ops: data._debug });
  }
  renderDebugHistory();
  // Also store JSON in hidden pre for raw view if needed
  const pre = document.getElementById('debug-json');
  if (pre) {
    try {
      var clean = {};
      for (var key in data) {
        if (data.hasOwnProperty(key) && key !== '_debug') {
          clean[key] = data[key];
        }
      }
      pre.textContent = JSON.stringify(clean, null, 2);
    } catch (e) {
      pre.textContent = String(data);
    }
  }
}

function escHtml(str) {
  if (str == null) return '';
  const d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

// ===== SEND MESSAGE =====

async function sendMessage() {
  if (isProcessing) return;
  const inputField = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const messageText = inputField.value.trim();
  if (!messageText) return;

  appendMsg(escHtml(messageText), 'user');
  inputField.value = "";
  sendBtn.disabled = true;
  inputField.disabled = true;
  isProcessing = true;
  document.body.classList.add('processing');

  showTyping();

  try {
    const response = await apiPost(API_URL_CHAT + "/play", {
      message: messageText,
      interesses_list: userProfile.interests || [],
      apelido: userProfile.name || 'Aluno',
      disciplina: messageText,
      mode: getModeLabel(currentMode)
    });

    let data;
    try {
      data = await response.json();
      if (!data || typeof data !== 'object') throw new Error('not an object');
    } catch {
      const raw = await response.text().catch(() => '');
      data = { tipo: 'resposta', resumo: raw.slice(0, 500), sugestoes: [] };
    }

    removeTyping();
    lastResponseData = data;
    updateDebugContent(data);
    const botBubble = appendMsg('', 'bot');
    renderizarRespostaPersonalizada(data, currentMode, botBubble);
    // Add red styling for blocked messages
    if (data._debug && Array.isArray(data._debug) && data._debug.some(function(d) { return d.tipo === 'bloqueio'; })) {
      botBubble.classList.add('blocked');
    }

  } catch (error) {
    console.error("Erro:", error);
    removeTyping();
    const errBubble = appendMsg('', 'bot');
    errBubble.innerHTML = `<i>Erro ao conectar ao servidor. Tente novamente.</i>`;
  } finally {
    sendBtn.disabled = false;
    inputField.disabled = false;
    isProcessing = false;
    document.body.classList.remove('processing');
    inputField.focus();
    document.getElementById('chat-history').scrollTop = document.getElementById('chat-history').scrollHeight;
  }
}

// ===== ANSWER CHECKING =====

function disableAllAnswers(parent) {
  if (!parent) return;
  var all = parent.querySelectorAll('.quiz-answer');
  for (var k = 0; k < all.length; k++) {
    all[k].classList.add('answered');
  }
}

function highlightCorrect(parent, correta) {
  if (!parent) return;
  var all = parent.querySelectorAll('.quiz-answer');
  for (var k = 0; k < all.length; k++) {
    if (all[k].getAttribute('data-letra') === correta || all[k].getAttribute('data-texto') === correta) {
      all[k].style.background = '#2E7D32';
      all[k].style.color = '#fff';
    }
  }
}

function isCorrectAnswer(el, correta) {
  var letra = el.getAttribute('data-letra');
  var texto = el.getAttribute('data-texto');
  return letra === correta || texto === correta;
}

function checkAnswer(el) {
  if (el.classList.contains('answered')) return;
  disableAllAnswers(el.parentElement);
  var letra = el.getAttribute('data-letra');
  var correta = el.getAttribute('data-correta');
  if (letra === correta) {
    el.style.background = '#2E7D32';
    el.style.color = '#fff';
  } else {
    el.style.background = '#C62828';
    el.style.color = '#fff';
    highlightCorrect(el.parentElement, correta);
  }
}

function checkQuizAnswer(el) {
  if (el.classList.contains('answered')) return;
  disableAllAnswers(el.parentElement);
  var texto = el.getAttribute('data-texto');
  var correta = el.getAttribute('data-correta');
  if (isCorrectAnswer(el, correta)) {
    el.style.background = '#2E7D32';
    el.style.color = '#fff';
  } else {
    el.style.background = '#C62828';
    el.style.color = '#fff';
    highlightCorrect(el.parentElement, correta);
  }
}

// ===== RENDER RESPONSE =====

function asArray(v) {
  if (Array.isArray(v)) return v.length > 0 ? v : null;
  if (v && typeof v === 'object') return [v];
  return null;
}

function textFallback(data) {
  return data.resumo || data.conteudo || data.texto || data.explicacao || data.descricao || data.pergunta || '';
}

function renderizarRespostaPersonalizada(data, mode, container) {
  let html = '';

  if (data.titulo) {
    html += `<h3>${escHtml(data.titulo)}</h3><hr>`;
  }

  switch (mode) {
    case 'RESUMO': {
      const txt = textFallback(data);
      if (txt) html += `<p>${escHtml(txt).replace(/\n/g, '<br>')}</p>`;
      else html += `<p>${escHtml(JSON.stringify(data))}</p>`;
      break;
    }

    case 'EXERCICIO': {
      const questoes = asArray(data.questoes || data.perguntas) || (data.pergunta ? [data] : null);
      if (questoes) {
        html += `<p style="margin-bottom:10px;color:#4A6EA8;font-size:13px;">Resolva as quest\u00f5es abaixo:</p>`;
        questoes.forEach((q, i) => {
          const pergunta = q.pergunta || q.nome || 'Quest\u00e3o';
          const altArr = asArray(q.alternativas) || [];
          const correta = q.resposta_correta || q.correta || '';
          html += `<div class="exercise-item"><h4>${i+1}. ${escHtml(pergunta)}</h4>`;
          altArr.forEach((alt, j) => {
            const letra = alt.letra || String.fromCharCode(65 + j);
            const texto = alt.texto || alt;
            html += `<div class="quiz-answer" data-letra="${escHtml(letra)}" data-texto="${escHtml(texto)}" data-correta="${escHtml(correta)}" onclick="checkAnswer(this)">${letra}) ${escHtml(texto)}</div>`;
          });
          html += `</div>`;
        });
      } else {
        const txt = textFallback(data);
        if (txt) html += `<p>${escHtml(txt).replace(/\n/g, '<br>')}</p>`;
        else html += `<p>${escHtml(JSON.stringify(data))}</p>`;
      }
      break;
    }

    case 'REVISAO': {
      const crono = asArray(data.cronograma || data.dias);
      if (crono) {
        html += `<p style="margin-bottom:10px;color:#4A6EA8;font-size:13px;">Cronograma de revis\u00e3o:</p>`;
        crono.forEach((item, i) => {
          const dia = item.dia || `Dia ${i+1}`;
          const assunto = item.assunto || item.titulo || '';
          const desc = item.descricao || '';
          html += `<div class="exercise-item"><h4>${escHtml(dia)}: ${escHtml(assunto)}</h4>${desc ? `<p>${escHtml(desc)}</p>` : ''}</div>`;
        });
      } else {
        const txt = textFallback(data);
        if (txt) html += `<p>${escHtml(txt).replace(/\n/g, '<br>')}</p>`;
        else html += `<p>${escHtml(JSON.stringify(data))}</p>`;
      }
      break;
    }

    case 'QUIZ': {
      const perguntas = asArray(data.perguntas || data.questoes) || (data.pergunta ? [data] : null);
      if (perguntas) {
        html += `<p style="margin-bottom:10px;color:#4A6EA8;font-size:13px;">Quiz r\u00e1pido:</p>`;
        perguntas.forEach((q, i) => {
          const pergunta = q.pergunta || q.question || 'Pergunta';
          const alternativas = asArray(q.alternativas) || [];
          const correta = q.resposta || q.correta || '';
          html += `<div class="quiz-item"><h4>${i+1}. ${escHtml(pergunta)}</h4>`;
          alternativas.forEach((alt, j) => {
            const texto = typeof alt === 'string' ? alt : (alt.texto || alt.label || String(alt));
            const letra = String.fromCharCode(65 + j);
            html += `<div class="quiz-answer" data-letra="${escHtml(letra)}" data-texto="${escHtml(texto)}" data-correta="${escHtml(correta)}" onclick="checkQuizAnswer(this)">${letra}) ${escHtml(texto)}</div>`;
          });
          html += `</div>`;
        });
      } else {
        const txt = textFallback(data);
        if (txt) html += `<p>${escHtml(txt).replace(/\n/g, '<br>')}</p>`;
        else html += `<p>${escHtml(JSON.stringify(data))}</p>`;
      }
      break;
    }

    default: {
      const txt = textFallback(data);
      if (txt) html += `<p>${escHtml(txt).replace(/\n/g, '<br>')}</p>`;
      else html += `<p>${escHtml(JSON.stringify(data))}</p>`;
    }
  }

  container.innerHTML = html;

  // Visual content inside bubble
  if (data.visual) {
    renderVisualContent(data.visual, container);
  }

  // Suggestions LAST
  if (Array.isArray(data.sugestoes) && data.sugestoes.length > 0) {
    const sugsDiv = document.createElement('div');
    const hr = document.createElement('hr');
    sugsDiv.appendChild(hr);
    const label = document.createElement('p');
    label.style.cssText = 'font-size:13px;color:#4A6EA8;font-weight:700;margin:8px 0 6px;';
    label.textContent = 'Sugest\u00f5es:';
    sugsDiv.appendChild(label);
    const list = document.createElement('div');
    list.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;';
    data.sugestoes.forEach(s => {
      const chip = document.createElement('span');
      chip.className = 'sugestao-chip';
      chip.textContent = s;
      chip.onclick = function() { clickSugestao(this); };
      list.appendChild(chip);
    });
    sugsDiv.appendChild(list);
    container.appendChild(sugsDiv);
  }
}

// ===== CLICKABLE SUGESTÕES =====

async function clickSugestao(el) {
  if (isProcessing) return;
  const text = el.textContent;
  const input = document.getElementById('message-input');
  if (input) {
    input.value = text;
    await sendMessage();
  }
  const area = document.getElementById('chat-history');
  if (area) area.scrollTop = area.scrollHeight;
}

// ===== VISUAL CONTENT RENDERING =====

function renderVisualContent(visual, container) {
  if (!visual) return;
  try {
    if (visual.mindmap && visual.mindmap.length > 10) renderMindmap(visual.mindmap, container);
    if (visual.flashcards && Array.isArray(visual.flashcards) && visual.flashcards.length > 0) renderFlashcards(visual.flashcards, container);
    if (visual.chart && typeof visual.chart === 'object' && visual.chart.type && visual.chart.data) renderChart(visual.chart, container);
    if (visual.mermaid && visual.mermaid.length > 5) renderMermaid(visual.mermaid, container);
  } catch (e) {
    console.warn('Visual render error:', e);
  }
}

function renderMindmap(markdown, container) {
  if (!markdown || markdown.length < 10) return;
  const wrap = document.createElement('div');
  wrap.className = 'visual-container mindmap';
  wrap.style.cssText = 'width:100%;min-height:260px;position:relative;';
  wrap.innerHTML = '<div class="markmap-loading">Carregando mapa mental...</div>';
  container.appendChild(wrap);
  const script = document.createElement('script');
  script.type = 'text/template';
  script.textContent = markdown;
  wrap.appendChild(script);
  setTimeout(() => {
    try {
      const mm = window.markmap;
      if (mm && mm.Transformer && mm.Markmap) {
        wrap.innerHTML = '';
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.width = '100%';
        svg.style.height = '260px';
        wrap.appendChild(svg);
        const t = new mm.Transformer();
        const root = t.transform(markdown).root;
        mm.Markmap.create(svg, null, root);
      }
    } catch (e) {
      console.warn('Mindmap failed:', e);
    }
    setTimeout(() => {
      if (wrap.querySelector('.markmap-loading')) {
        wrap.innerHTML = '<div style="padding:12px;font-size:14px;color:#1A3560;white-space:pre-wrap;font-family:monospace;">' + escHtml(markdown) + '</div>';
      }
    }, 3000);
  }, 100);
}

function renderFlashcards(cards, container) {
  const grid = document.createElement('div');
  grid.className = 'flashcard-grid';
  var hasCards = false;
  cards.forEach(card => {
    var front = card.front || card.pergunta || card.question || card.titulo || card.title || card.frente || card.conceito || card.nome || '';
    var back = card.back || card.resposta || card.answer || card.descricao || card.description || card.verso || card.definicao || card.definition || card.explicacao || '';
    if (!front && !back) return;
    hasCards = true;
    const fc = document.createElement('div');
    fc.className = 'flashcard';
    fc.innerHTML = '<div class="flashcard-inner"><div class="flashcard-front">' + escHtml(front) + '</div><div class="flashcard-back">' + escHtml(back) + '</div></div>';
    fc.addEventListener('click', () => fc.classList.toggle('flipped'));
    grid.appendChild(fc);
  });
  if (!hasCards) return;
  container.appendChild(grid);
  const hint = document.createElement('div');
  hint.className = 'flashcard-hint';
  hint.textContent = 'Clique nos cards para virar';
  container.appendChild(hint);
}

function renderChart(config, container) {
  if (typeof Chart === 'undefined') return;
  const id = 'chart-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  const wrap = document.createElement('div');
  wrap.className = 'visual-container chart-wrap';
  const canvas = document.createElement('canvas');
  canvas.id = id;
  wrap.appendChild(canvas);
  container.appendChild(wrap);
  try {
    const ctx = canvas.getContext('2d');
    new Chart(ctx, config);
  } catch (e) {
    console.warn("Chart error:", e);
    wrap.innerHTML = '<p style="color:#8AAAC8;text-align:center;">Erro ao renderizar gr\u00e1fico</p>';
  }
}

function renderMermaid(diagram, container) {
  if (typeof mermaid === 'undefined' || !mermaid.run) {
    const pre = document.createElement('pre');
    pre.style.cssText = 'font-size:12px;color:#4A6EA8;white-space:pre-wrap;background:rgba(255,255,255,0.5);padding:10px;border-radius:8px;';
    pre.textContent = diagram;
    container.appendChild(pre);
    return;
  }
  const id = 'mermaid-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  const wrap = document.createElement('div');
  wrap.className = 'visual-container mermaid-wrap';
  const div = document.createElement('div');
  div.className = 'mermaid';
  div.id = id;
  div.textContent = diagram;
  wrap.appendChild(div);
  container.appendChild(wrap);
  mermaid.run({ nodes: [div] }).catch(function(e) {
    console.warn('Mermaid failed:', e);
    wrap.innerHTML = '<pre style="font-size:12px;color:#4A6EA8;">' + escHtml(diagram) + '</pre>';
  });
}
