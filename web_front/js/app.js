const userProfile = { id: '', name: '', grade: '', interests: [] };

function loadProfile() {
  try {
    const stored = JSON.parse(localStorage.getItem(profileStorageKey));
    if (stored) {
      userProfile.id = stored.id || '';
      userProfile.name = stored.name || '';
      userProfile.grade = stored.grade || '';
      userProfile.interests = Array.isArray(stored.interests) ? stored.interests : [];
    }
  } catch (_) {
    localStorage.removeItem(profileStorageKey);
  }
}

function saveProfile() {
  localStorage.setItem(profileStorageKey, JSON.stringify(userProfile));
}

function normalizeText(text) {
  return String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function goTo(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById('screen-' + screen);
  if (el) el.classList.add('active');
  if (screen === 'chat') {
    document.getElementById('message-input').focus();
  }
  if (screen === 'onboarding-nome') {
    document.getElementById('user-name').focus();
  }
  if (screen === 'customizar') {
    setupCustomizer();
  }
  if (screen === 'principal') {
    applyProfile();
  }
}

// ===== ONBOARDING =====

function startOnboarding() {
  loadProfile();
  const nameInput = document.getElementById('user-name');
  if (nameInput) nameInput.value = userProfile.name;
  restoreSelections();
  goTo('onboarding-nome');
}

function nextFromName() {
  const nameInput = document.getElementById('user-name');
  const error = document.getElementById('name-error');
  const name = nameInput.value.trim();
  if (!name) {
    error.textContent = 'Digite seu nome para continuar.';
    nameInput.focus();
    return;
  }
  userProfile.name = name;
  saveProfile();
  error.textContent = '';
  goTo('onboarding-ano');
}

function selectGrade(grade, button) {
  userProfile.grade = grade;
  document.querySelectorAll('#grade-options .option-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  document.getElementById('grade-error').textContent = '';
}

async function nextFromGrade() {
  if (!userProfile.grade) {
    document.getElementById('grade-error').textContent = 'Escolha seu ano escolar para continuar.';
    return;
  }

  const name = userProfile.name.trim();
  try {
    const aluno = await apiGet(API_URL_ALUNO + "/username/" + encodeURIComponent(name));

    if (!aluno) {
      const createResponse = await apiPost(API_URL_ALUNO + "/save", {
        apelido: name,
        ano_escolar: userProfile.grade
      });
      const created = await createResponse.json();
      userProfile.id = created.id;
      saveProfile();
      goTo('onboarding-interesses');
    } else {
      userProfile.id = aluno.id;

      const interestsData = await apiGet(API_URL_ALUNO + "/" + aluno.id + "/interesses");
      if (interestsData && interestsData.interesses) {
        userProfile.interests = interestsData.interesses.map(i => i.nome);
      } else {
        userProfile.interests = [];
      }

      saveProfile();
      applyProfile();
      goTo('principal');
    }
  } catch (error) {
    console.error("Erro:", error);
    document.getElementById('grade-error').textContent = 'Erro ao conectar com o servidor. Tente novamente.';
  }
}

function toggleInterest(button) {
  button.classList.toggle('active');
  document.getElementById('interest-error').textContent = '';
}

async function finishOnboarding() {
  const selected = Array.from(document.querySelectorAll('#interest-options .option-btn.active'))
    .map(btn => btn.dataset.interest);
  const notes = document.getElementById('interest-notes').value
    .split(',').map(s => s.trim()).filter(Boolean);

  userProfile.interests = [...new Set([...selected, ...notes])];

  if (userProfile.interests.length === 0) {
    document.getElementById('interest-error').textContent = 'Escolha ou escreva pelo menos um interesse.';
    return;
  }

  try {
    await apiPost(API_URL_ALUNO + "/interesses/save", {
      aluno_id: userProfile.id,
      interesses: userProfile.interests
    });
  } catch (error) {
    console.error("Erro ao salvar interesses:", error);
  }

  saveProfile();
  applyProfile();
  goTo('principal');
}

function restoreSelections() {
  document.querySelectorAll('#grade-options .option-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.trim() === userProfile.grade);
  });
  document.querySelectorAll('#interest-options .option-btn').forEach(btn => {
    btn.classList.toggle('active', userProfile.interests.includes(btn.dataset.interest));
  });
}

function applyProfile() {
  loadProfile();
  const welcomeTitle = document.getElementById('welcome-title');
  const welcomeSubtitle = document.getElementById('welcome-subtitle');
  if (!welcomeTitle || !welcomeSubtitle || !userProfile.name) return;

  const interestsText = userProfile.interests.length
    ? ` Vou trazer exemplos com ${userProfile.interests.slice(0, 3).join(', ')}.`
    : '';

  welcomeTitle.textContent = `Oi, ${userProfile.name.toLocaleUpperCase()}!`;
  welcomeSubtitle.textContent = `${userProfile.grade ? userProfile.grade + ' - ' : ''}pronto para evoluir hoje?${interestsText}`;
}

// ===== SIDEBAR =====

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

// ===== INIT =====

document.addEventListener('DOMContentLoaded', () => {
  applyProfile();

  document.getElementById("user-name").addEventListener("keypress", function(e) {
    if (e.key === "Enter") { e.preventDefault(); nextFromName(); }
  });

  document.getElementById("message-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") { e.preventDefault(); sendMessage(); }
  });
});
