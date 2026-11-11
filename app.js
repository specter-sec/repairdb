import Fuse from './assets/fuse.min.mjs';

const brands = ['Samsung', 'Xiaomi', 'Infinix', 'Tecno', 'Oppo', 'Vivo', 'iPhone'];
const brandFiles = ['samsung', 'xiaomi', 'infinix', 'tecno', 'oppo', 'vivo', 'iphone'];
const $ = (selector) => document.querySelector(selector);
const resultsEl = $('#results');
const searchInput = $('#search');
const brandSelect = $('#brand-filter');
const symptomSelect = $('#symptom-filter');
const difficultySelect = $('#difficulty-filter');
const dialog = $('#detail-dialog');
const detailContent = $('#detail-content');
let allGuides = [];
let fuse;

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
})[char]);

function setTheme(dark) {
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.body.classList.toggle('dark', dark);
  const toggle = $('#theme-toggle');
  toggle.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  $('.theme-label').textContent = dark ? 'Light mode' : 'Dark mode';
  try { localStorage.setItem('repairdb-theme', dark ? 'dark' : 'light'); } catch { /* Browsing still works when storage is disabled. */ }
}

function renderFilters() {
  for (const brand of brands) brandSelect.add(new Option(brand, brand));
  const symptoms = [...new Set(allGuides.map((guide) => guide.symptom))].sort();
  for (const symptom of symptoms) symptomSelect.add(new Option(symptom.replace(/^./, (c) => c.toUpperCase()), symptom));
}

function cardTemplate(guide) {
  return `<article class="guide-card">
    <div class="card-topline"><span class="brand-tag">${escapeHtml(guide.brand)}</span><span class="difficulty-tag">${escapeHtml(guide.difficulty)}</span></div>
    <h3>${escapeHtml(guide.title)}</h3><p class="model-line">${escapeHtml(guide.model)}</p>
    <span class="symptom-label">${escapeHtml(guide.symptom)}</span>
    <div class="card-bottom"><span>Sample · parts-only range</span><button type="button" data-open="${escapeHtml(guide.id)}" aria-label="Open guide: ${escapeHtml(guide.title)}, ${escapeHtml(guide.model)}">View guide&nbsp; →</button></div>
  </article>`;
}

function filteredGuides() {
  let candidates = allGuides;
  const query = searchInput.value.trim();
  if (query) candidates = fuse.search(query).map((result) => result.item);
  return candidates.filter((guide) =>
    (!brandSelect.value || guide.brand === brandSelect.value) &&
    (!symptomSelect.value || guide.symptom === symptomSelect.value) &&
    (!difficultySelect.value || guide.difficulty === difficultySelect.value)
  );
}

function render() {
  const guides = filteredGuides();
  resultsEl.innerHTML = guides.map(cardTemplate).join('');
  $('#result-count').textContent = `${guides.length} ${guides.length === 1 ? 'guide' : 'guides'} shown`;
  $('#empty-state').hidden = guides.length !== 0;
  resultsEl.hidden = guides.length === 0;
}

function detailTemplate(guide) {
  const list = (items) => items.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  const cost = guide.estimated_cost_usd_parts_only;
  return `<p class="eyebrow">${escapeHtml(guide.brand)} / ${escapeHtml(guide.symptom)}</p>
    <h2 id="detail-title">${escapeHtml(guide.title)}</h2>
    <p class="detail-meta">${escapeHtml(guide.model)} · ${escapeHtml(guide.difficulty)} · Educational example</p>
    <div class="detail-warning"><strong>Training example only.</strong> Not a verified issue for this brand or model. Cost is a sample USD parts-only range, not a quote.</div>
    <section class="detail-block"><h3>Safe checks to try first</h3><ol>${list(guide.safe_diagnostic_steps)}</ol></section>
    <section class="detail-block"><h3>Components that may be involved</h3><ul>${list(guide.likely_components)}</ul></section>
    <section class="detail-block"><h3>Tools / references</h3><ul>${list(guide.tools)}</ul></section>
    <p class="cost-note"><strong>Illustrative parts-only range:</strong> $${Number(cost.min).toFixed(0)}–$${Number(cost.max).toFixed(0)} USD. Actual parts, labor, availability, and repairability vary widely.</p>
    <section class="detail-block"><h3>Safety notes</h3><p>${escapeHtml(guide.safety_notes)}</p></section>`;
}

resultsEl.addEventListener('click', (event) => {
  const button = event.target.closest('[data-open]');
  if (!button) return;
  const guide = allGuides.find((item) => item.id === button.dataset.open);
  if (!guide) return;
  detailContent.innerHTML = detailTemplate(guide);
  dialog.showModal();
  $('.dialog-close').focus();
});
$('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
$('#theme-toggle').addEventListener('click', () => setTheme(document.documentElement.dataset.theme !== 'dark'));
searchInput.addEventListener('input', render);
[brandSelect, symptomSelect, difficultySelect].forEach((select) => select.addEventListener('change', render));
function clearFilters() {
  searchInput.value = '';
  brandSelect.value = '';
  symptomSelect.value = '';
  difficultySelect.value = '';
  render();
  searchInput.focus();
}
$('#clear-filters').addEventListener('click', clearFilters);
$('#empty-clear').addEventListener('click', clearFilters);
document.addEventListener('keydown', (event) => {
  if (event.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
    event.preventDefault(); searchInput.focus();
  }
});

let savedTheme = null;
try { savedTheme = localStorage.getItem('repairdb-theme'); } catch { /* Use the system preference. */ }
setTheme(savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches);
try {
  const datasets = await Promise.all(brandFiles.map(async (file) => {
    const response = await fetch(`./data/${file}.json`);
    if (!response.ok) throw new Error(`Could not load ${file}.json`);
    return response.json();
  }));
  allGuides = datasets.flat();
  renderFilters();
  fuse = new Fuse(allGuides, {
    keys: ['title', 'brand', 'model', 'symptom', 'likely_components', 'safe_diagnostic_steps'],
    threshold: 0.35,
    ignoreLocation: true,
    minMatchCharLength: 2,
  });
  $('#hero-count').textContent = String(allGuides.length);
  render();
} catch (error) {
  console.error('RepairDB sample data failed to load:', error);
  $('#result-count').textContent = 'Data unavailable';
  $('#load-error').hidden = false;
  resultsEl.hidden = true;
}
