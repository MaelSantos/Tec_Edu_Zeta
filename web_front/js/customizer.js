const profileStorageKey = 'nexTutorUserProfile';
const customizationStorageKey = 'nexTutorOtterCustomization';

let customState = { headIndex: 0, bodyIndex: 0 };
let headOptions = [];
let bodyOptions = [];

const headCatalog = [
  { label: 'Sem chap\u00e9u', className: 'head-none', interests: [] },
  { label: 'Bon\u00e9 esportivo', className: 'hat-cap', interests: ['Esportes'] },
  { label: 'Headset gamer', className: 'hat-headset', interests: ['Jogos', 'M\u00fasica', 'Tecnologia'] },
  { label: 'Boina art\u00edstica', className: 'hat-beret', interests: ['Arte'] },
  { label: '\u00d3culos VR', className: 'hat-vr', interests: ['Tecnologia', 'Jogos'] },
  { label: '\u00d3culos de cinema', className: 'hat-film', interests: ['Filmes e s\u00e9ries', 'Filmes'] }
];

const bodyCatalog = [
  { label: 'Sem roupa', className: 'body-none', interests: [] },
  { label: 'Camisa de time', className: 'body-jersey', interests: ['Esportes'] },
  { label: 'Moletom gamer', className: 'body-hoodie', interests: ['Jogos', 'M\u00fasica'] },
  { label: 'Avental criativo', className: 'body-apron', interests: ['Arte'] },
  { label: 'Jaqueta tech', className: 'body-tech', interests: ['Tecnologia'] },
  { label: 'Blusa cora\u00e7\u00e3o', className: 'body-heart', interests: ['Filmes e s\u00e9ries', 'Filmes', 'M\u00fasica'] }
];

function loadCustomization() {
  try {
    const stored = JSON.parse(localStorage.getItem(customizationStorageKey));
    if (stored) {
      customState.headIndex = Number(stored.headIndex) || 0;
      customState.bodyIndex = Number(stored.bodyIndex) || 0;
    }
  } catch (_) {
    localStorage.removeItem(customizationStorageKey);
  }
}

function matchesInterest(option) {
  if (!option.interests.length) return true;
  const profileInterests = (userProfile.interests || []).map(normalizeText);
  return option.interests.some(interest =>
    profileInterests.some(pi =>
      pi.includes(normalizeText(interest)) || normalizeText(interest).includes(pi)
    )
  );
}

function getUnlockedOptions(catalog) {
  const unlocked = catalog.filter(matchesInterest);
  return unlocked.length > 1 ? unlocked : catalog.slice(0, 3);
}

function setupCustomizer() {
  loadProfile();
  loadCustomization();

  headOptions = getUnlockedOptions(headCatalog);
  bodyOptions = getUnlockedOptions(bodyCatalog);
  customState.headIndex = customState.headIndex % headOptions.length;
  customState.bodyIndex = customState.bodyIndex % bodyOptions.length;

  const list = document.getElementById('custom-interest-list');
  const note = document.getElementById('custom-note');
  if (list) {
    list.innerHTML = '';
    const interests = userProfile.interests.length ? userProfile.interests : ['Jogos', 'Tecnologia', 'Arte'];
    interests.forEach(i => {
      const chip = document.createElement('span');
      chip.className = 'custom-interest-chip';
      chip.textContent = i;
      list.appendChild(chip);
    });
  }
  if (note) {
    note.textContent = userProfile.interests.length
      ? 'As op\u00e7\u00f5es liberadas v\u00eam dos interesses que voc\u00ea escolheu na p\u00e1gina de perfil.'
      : 'Sem interesses salvos ainda, deixei algumas op\u00e7\u00f5es iniciais para testar.';
  }
  renderCustomizer();
}

function renderCustomizer() {
  const headLayer = document.getElementById('head-layer');
  const bodyLayer = document.getElementById('body-layer');
  const headLabel = document.getElementById('head-label');
  const bodyLabel = document.getElementById('body-label');

  if (!headLayer || !bodyLayer || !headOptions.length || !bodyOptions.length) return;

  const head = headOptions[customState.headIndex];
  const body = bodyOptions[customState.bodyIndex];
  headLayer.innerHTML = `<div class="head-item ${head.className}"></div>`;
  bodyLayer.innerHTML = `<div class="body-item ${body.className}"></div>`;
  if (headLabel) headLabel.textContent = `Cabe\u00e7a: ${head.label}`;
  if (bodyLabel) bodyLabel.textContent = `Corpo: ${body.label}`;
}

function cycleCustomPart(part, direction) {
  const options = part === 'head' ? headOptions : bodyOptions;
  if (!options.length) return;
  if (part === 'head') {
    customState.headIndex = (customState.headIndex + direction + options.length) % options.length;
  } else {
    customState.bodyIndex = (customState.bodyIndex + direction + options.length) % options.length;
  }
  renderCustomizer();
}

function saveCustomization() {
  localStorage.setItem(customizationStorageKey, JSON.stringify(customState));
  goTo('principal');
}
