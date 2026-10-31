'use strict';

// ============================================================
// SPLASH
// ============================================================
(function(){
  const splash = document.getElementById('splash');
  if (!splash) return;
  const MIN_SHOW_MS = 1400;
  const startTime = performance.now();
  let hidden = false;
  function hideSplash(){
    if (hidden) return;
    hidden = true;
    const remaining = Math.max(0, MIN_SHOW_MS - (performance.now() - startTime));
    setTimeout(() => {
      splash.classList.add('hidden');
      setTimeout(() => { try { splash.remove(); } catch(e){} }, 700);
    }, remaining);
  }
  if (document.readyState === 'complete') hideSplash();
  else {
    window.addEventListener('load', hideSplash);
    setTimeout(hideSplash, 3500);
  }
})();

// ============================================================
// THEME
// ============================================================
const THEME_KEY = 'shared_files_theme';
const themeButtons = document.querySelectorAll('.theme-toggle button');

function getSavedTheme(){
  try {
    const v = localStorage.getItem(THEME_KEY);
    return (v === 'dark' || v === 'light') ? v : 'dark';
  } catch { return 'dark'; }
}
function applyTheme(theme){
  document.documentElement.setAttribute('data-theme', theme);
  themeButtons.forEach(b => b.classList.toggle('active', b.dataset.themeValue === theme));
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) metaThemeColor.setAttribute('content', theme === 'light' ? '#ffffff' : '#000000');
}
themeButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const theme = btn.dataset.themeValue;
    try { localStorage.setItem(THEME_KEY, theme); } catch {}
    applyTheme(theme);
  });
});
applyTheme(getSavedTheme());

// ============================================================
// HIDDEN TOGGLE
// ============================================================
const HIDDEN_KEY = 'shared_files_hidden';
const hiddenBtn = document.getElementById('hiddenBtn');

const EYE_OPEN = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
const EYE_CLOSED = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';

function isHiddenEnabled(){
  try {
    const u = new URL(location.href);
    if (u.searchParams.get('hidden') === '1') return true;
    if (u.searchParams.get('hidden') === '0') return false;
  } catch {}
  try { return localStorage.getItem(HIDDEN_KEY) === '1'; } catch { return false; }
}
function setHiddenEnabled(v){
  try { localStorage.setItem(HIDDEN_KEY, v ? '1' : '0'); } catch {}
}
function applyHiddenButton(){
  const on = isHiddenEnabled();
  hiddenBtn.classList.toggle('active', on);
  hiddenBtn.title = on ? 'Hide hidden files' : 'Show hidden files';
  hiddenBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
  hiddenBtn.querySelector('svg').innerHTML = on ? EYE_OPEN : EYE_CLOSED;
}
function withHiddenParam(url){
  try {
    const u = new URL(url, location.origin);
    if (isHiddenEnabled()) u.searchParams.set('hidden', '1');
    else u.searchParams.delete('hidden');
    const q = u.searchParams.toString();
    return u.pathname + (q ? '?' + q : '');
  } catch { return url; }
}
hiddenBtn.addEventListener('click', () => {
  const next = !isHiddenEnabled();
  setHiddenEnabled(next);
  try {
    const u = new URL(location.href);
    if (next) u.searchParams.set('hidden', '1');
    else u.searchParams.delete('hidden');
    history.replaceState(history.state, '', u.pathname + u.search);
  } catch {}
  applyHiddenButton();
  navigateTo(location.pathname, false);
});
applyHiddenButton();

// ============================================================
// FULLSCREEN
// ============================================================
const fsFab = document.getElementById('fsFab');
function isFS(){
  return !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
}
function requestFS(el){
  const fn = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
  if (!fn) return;
  try {
    const p = fn.call(el, { navigationUI: 'hide' });
    if (p && p.catch) p.catch(() => {});
  } catch(e){}
}
function exitFS(){
  fsGuardActive = false;
  const fn = document.exitFullscreen || document.webkitExitFullscreen || document.msExitFullscreen;
  if (!fn) return;
  try { const p = fn.call(document); if (p && p.catch) p.catch(() => {}); } catch(e){}
}
function updateFab(){
  const fs = isFS();
  if (fs) {
    fsFab.querySelector('svg').innerHTML =
      '<path d="M9 3v6H3"/>' +
      '<path d="M15 3h6v6"/>' +
      '<path d="M3 15h6v6"/>' +
      '<path d="M21 15v6h-6"/>';
  } else {
    fsFab.querySelector('svg').innerHTML =
      '<path d="M3 9V3h6"/>' +
      '<path d="M15 3h6v6"/>' +
      '<path d="M9 21H3v-6"/>' +
      '<path d="M21 15v6h-6"/>';
  }
  fsFab.title = fs ? 'Exit fullscreen' : 'Fullscreen';
  fsFab.classList.toggle('hidden', document.getElementById('viewer').classList.contains('open'));
}
fsFab.addEventListener('click', () => {
  if (isFS()) exitFS();
  else requestFS(document.documentElement);
});

// ------------------------------------------------------------
// Fullscreen history guard
// ------------------------------------------------------------
const FS_GUARD_KEY = '__fs_guard__';
let fsGuardActive = false;
let fsGuardPushed = false;
let lastFsGuardTime = 0;

function pushFsGuard(){
  if (fsGuardPushed) return;
  try {
    history.pushState(
      { ...(history.state || {}), [FS_GUARD_KEY]: true, url: location.pathname + location.search },
      '',
      location.href
    );
    fsGuardPushed = true;
    fsGuardActive = true;
    lastFsGuardTime = Date.now();
  } catch(e){}
}

function handleFsGuardPop(){
  const now = Date.now();

  if (fsGuardActive && now - lastFsGuardTime < 500) {
    fsGuardActive = false;
    fsGuardPushed = false;
    return false;
  }

  if (isFS() && fsGuardActive) {
    lastFsGuardTime = now;
    fsGuardPushed = false;
    pushFsGuard();
    const el = document.fullscreenElement
            || document.webkitFullscreenElement
            || document.msFullscreenElement;
    if (el) requestFS(el);
    else requestFS(document.documentElement);
    return true;
  }

  if (!isFS()) {
    fsGuardActive = false;
    fsGuardPushed = false;
  }
  return false;
}

function onFullscreenChange(){
  const fs = isFS();

  if (fs) {
    pushFsGuard();
  } else {
    fsGuardPushed = false;
    fsGuardActive = false;
    refreshFileList();
  }

  updateFab();
  viewer.classList.toggle('video-fullscreen', fs);
}
document.addEventListener('fullscreenchange', onFullscreenChange);
document.addEventListener('webkitfullscreenchange', onFullscreenChange);
updateFab();

// ============================================================
// VIEW TOGGLE
// ============================================================
const STORAGE_KEY = 'shared_files_view';
function applyView(view) {
  const isMobile = window.matchMedia('(max-width: 640px)').matches;
  const effective = isMobile ? 'list' : view;
  document.body.classList.remove('view-grid', 'view-list');
  document.body.classList.add('view-' + effective);
  document.querySelectorAll('.view-toggle button').forEach(b => {
    b.classList.toggle('active', b.dataset.view === effective);
  });
}
function getSavedView() {
  try { return localStorage.getItem(STORAGE_KEY) || 'grid'; } catch { return 'grid'; }
}
function bindViewToggle(){
  document.querySelectorAll('.view-toggle button').forEach(btn => {
    if (btn.dataset.bound === '1') return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', () => {
      const view = btn.dataset.view;
      try { localStorage.setItem(STORAGE_KEY, view); } catch {}
      applyView(view);
    });
  });
}
bindViewToggle();
applyView(getSavedView());
let rt;
window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => applyView(getSavedView()), 100); });

// ============================================================
// RESUME HELPERS
// ============================================================
const RESUME_PREFIX = 'sf_resume:';

function resumeKeyFor(src) {
  try {
    const u = new URL(src, location.origin);
    return RESUME_PREFIX + u.pathname;
  } catch {
    return RESUME_PREFIX + src;
  }
}
function saveResumeTime(src, time, duration) {
  if (!src) return;
  if (!isFinite(time) || time < 2) return;
  if (isFinite(duration) && duration > 0 && time > duration - 5) {
    clearResumeTime(src);
    return;
  }
  try {
    localStorage.setItem(resumeKeyFor(src), JSON.stringify({
      t: time,
      d: isFinite(duration) ? duration : 0,
      at: Date.now(),
    }));
  } catch (e) {}
}
function loadResumeTime(src) {
  if (!src) return 0;
  try {
    const raw = localStorage.getItem(resumeKeyFor(src));
    if (!raw) return 0;
    const obj = JSON.parse(raw);
    if (obj.at && Date.now() - obj.at > 30 * 24 * 3600 * 1000) {
      clearResumeTime(src);
      return 0;
    }
    return obj.t || 0;
  } catch { return 0; }
}
function clearResumeTime(src) {
  if (!src) return;
  try { localStorage.removeItem(resumeKeyFor(src)); } catch (e) {}
}

// ============================================================
// PICTURE PRESETS
// ============================================================
const PICTURE_STORAGE_KEY = 'sf_picture_settings';
const DEFAULT_PICTURE = {
  contrast: 1.10,
  saturate: 1.15,
  brightness: 1.00,
  sepia: 0.00,
};

const PICTURE_PRESET_LIST = [
  { key: 'off',       name: 'Off',         desc: 'Original image',           values: { contrast: 1.00, saturate: 1.00, brightness: 1.00, sepia: 0.00 } },
  { key: 'balanced',  name: 'Balanced',    desc: 'Best for most content',    values: { contrast: 1.10, saturate: 1.15, brightness: 1.00, sepia: 0.00 } },
  { key: 'punchy',    name: 'Punchy',      desc: 'Sports, docs, nature',     values: { contrast: 1.20, saturate: 1.25, brightness: 1.00, sepia: 0.00 } },
  { key: 'vivid',     name: 'Vivid',       desc: 'Maximum pop',              values: { contrast: 1.30, saturate: 1.30, brightness: 1.02, sepia: 0.03 } },
  { key: 'night',     name: 'Night',       desc: 'Dim room, no eye strain',  values: { contrast: 1.15, saturate: 1.10, brightness: 0.95, sepia: 0.00 } },
  { key: 'cinema',    name: 'Cinema',      desc: 'Movies, film look',        values: { contrast: 1.08, saturate: 1.10, brightness: 1.00, sepia: 0.00 } },
  { key: 'animation', name: 'Animation',   desc: 'Cartoons, bright colors',  values: { contrast: 1.12, saturate: 1.25, brightness: 1.02, sepia: 0.00 } },
  { key: 'anime',     name: 'Anime',       desc: 'Vivid with warm tint',     values: { contrast: 1.15, saturate: 1.30, brightness: 1.02, sepia: 0.02 } },
  { key: 'sport',     name: 'Sport',       desc: 'Fast action, sharp',       values: { contrast: 1.10, saturate: 1.15, brightness: 1.00, sepia: 0.00 } },
  { key: 'bw',        name: 'B&W Classic', desc: 'Black and white films',    values: { contrast: 1.15, saturate: 0.00, brightness: 1.05, sepia: 0.00 } },
  { key: 'dark-room', name: 'Dark Room',   desc: 'Pitch-black environment',  values: { contrast: 1.15, saturate: 1.10, brightness: 0.90, sepia: 0.00 } },
  { key: 'hdr',       name: 'HDR→SDR',     desc: 'HDR content on SDR screen',values: { contrast: 1.15, saturate: 1.25, brightness: 0.98, sepia: 0.00 } },
  { key: 'washed',    name: 'Washed Fix',  desc: 'Fix dull / faded video',   values: { contrast: 1.20, saturate: 1.30, brightness: 1.02, sepia: 0.02 } },
];

function loadPictureSettings() {
  try {
    const raw = localStorage.getItem(PICTURE_STORAGE_KEY);
    if (!raw) return { ...DEFAULT_PICTURE };
    return { ...DEFAULT_PICTURE, ...JSON.parse(raw) };
  } catch { return { ...DEFAULT_PICTURE }; }
}
function savePictureSettings(s) {
  try { localStorage.setItem(PICTURE_STORAGE_KEY, JSON.stringify(s)); } catch {}
}
function buildFilterString(s) {
  const parts = [];
  if (s.contrast !== 1)   parts.push(`contrast(${s.contrast})`);
  if (s.saturate !== 1)   parts.push(`saturate(${s.saturate})`);
  if (s.brightness !== 1) parts.push(`brightness(${s.brightness})`);
  if (s.sepia !== 0)      parts.push(`sepia(${s.sepia})`);
  return parts.length ? parts.join(' ') : 'none';
}
function applyPictureTo(el, s) {
  if (!el) return;
  el.style.filter = buildFilterString(s);
}

const globalPicture = loadPictureSettings();

// ============================================================
// MEDIA VIEWER
// ============================================================
const viewer    = document.getElementById('viewer');
const vTitle    = document.getElementById('vTitle');
const vMeta     = document.getElementById('vMeta');
const vContent  = document.getElementById('vContent');
const vDownload = document.getElementById('vDownload');
const vClose    = document.getElementById('vClose');
let currentPlayerCleanup = null;

function openViewer(data) {
  vTitle.textContent = data.name;
  vMeta.textContent = data.size || '';
  vDownload.href = data.url;
  vContent.innerHTML = '';
  if (currentPlayerCleanup) { try { currentPlayerCleanup(); } catch(e){} currentPlayerCleanup = null; }

  const kind = data.kind;
  const src  = data.url;

  if (kind === 'image') {
    const img = document.createElement('img');
    img.src = src; img.alt = data.name;
    applyPictureTo(img, globalPicture);
    vContent.appendChild(img);
  } else if (kind === 'video') {
    const r = buildVideoPlayer(src, data.name, data.quality || '', data.qualityTag || '');
    currentPlayerCleanup = r.cleanup;
    vContent.appendChild(r.el);
  } else if (kind === 'audio') {
    const r = buildAudioPlayer(src, data.name);
    currentPlayerCleanup = r.cleanup;
    vContent.appendChild(r.el);
  } else if (kind === 'pdf') {
    const iframe = document.createElement('iframe');
    iframe.src = src;
    vContent.appendChild(iframe);
  } else if (kind === 'text') {
    const pre = document.createElement('pre');
    pre.textContent = 'Loading...';
    vContent.appendChild(pre);
    fetch(src).then(r => r.text()).then(t => { pre.textContent = t; })
             .catch(() => { pre.textContent = 'Could not load file.'; });
  }

  viewer.classList.add('open');
  document.body.style.overflow = 'hidden';
  updateFab();
}

function closeViewer() {
  viewer.classList.remove('open');
  viewer.classList.remove('video-fullscreen');
  document.body.style.overflow = '';
  vContent.querySelectorAll('video, audio').forEach(m => {
    try {
      m.pause();
      m.removeAttribute('src');
      m.load();
    } catch(e){}
  });
  if (currentPlayerCleanup) { try { currentPlayerCleanup(); } catch(e){} currentPlayerCleanup = null; }
  setTimeout(() => { vContent.innerHTML = ''; }, 200);
  updateFab();
}

vClose.addEventListener('click', closeViewer);
viewer.addEventListener('click', (e) => {
  if (e.target === viewer || e.target.classList.contains('viewer-body')) closeViewer();
});
document.addEventListener('keydown', (e) => {
  if (!viewer.classList.contains('open')) return;
  if (e.key === 'Escape' && !isFS()) closeViewer();
});

// ============================================================
// SPA NAV
// ============================================================
let navInProgress = false;

async function navigateTo(url, pushState = true) {
  if (navInProgress) return;
  navInProgress = true;
  const target = withHiddenParam(url);
  try {
    const res = await fetch(target, {
      headers: { 'X-Requested-With': 'spa-nav' },
      cache: 'no-store'
    });
    if (!res.ok) { window.location.href = target; return; }
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');

    const newList = doc.getElementById('fileList');
    const oldList = document.getElementById('fileList');
    if (newList && oldList) oldList.replaceWith(newList);

    const newHeader = doc.querySelector('header');
    const oldHeader = document.querySelector('header');
    if (newHeader && oldHeader) oldHeader.replaceWith(newHeader);

    const newStat = doc.querySelector('.stat');
    const oldStat = document.querySelector('.stat');
    if (newStat && oldStat) oldStat.replaceWith(newStat);

    const newEmpty = doc.querySelector('.empty');
    const oldEmpty = document.querySelector('.empty');
    if (newEmpty && oldEmpty) oldEmpty.replaceWith(newEmpty);
    else if (newEmpty && !oldEmpty) {
      const listParent = document.getElementById('fileList')?.parentNode;
      if (listParent) listParent.appendChild(newEmpty);
    } else if (!newEmpty && oldEmpty) {
      oldEmpty.remove();
    }

    if (pushState) history.pushState({ url: target }, '', target);
    window.scrollTo({ top: 0, behavior: 'smooth' });

    const sInput = document.getElementById('search');
    if (sInput && sInput.value) {
      sInput.value = '';
      hideSearchPanel();
    }

    bindNavLinks();
    bindFileRows();
    rebindSearch();
    bindViewToggle();
  } catch (err) {
    window.location.href = target;
  } finally {
    navInProgress = false;
  }
}

function bindNavLinks() {
  document.querySelectorAll('a.nav-link').forEach(a => {
    if (a.dataset.navBound === '1') return;
    a.dataset.navBound = '1';
    a.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const href = a.getAttribute('href');
      if (!href) return;
      navigateTo(href);
    });
  });
}

function bindFileRows() {
  document.querySelectorAll('a.file-row').forEach(a => {
    if (a.dataset.bound === '1') return;
    a.dataset.bound = '1';
    if (!a.dataset.kind) return;
    a.addEventListener('click', (e) => {
      e.preventDefault();
      if (!isFS()) requestFS(document.documentElement);
      openViewer({
        url:  a.dataset.url,
        name: a.dataset.name,
        kind: a.dataset.kind,
        size: a.dataset.size,
        quality: a.dataset.quality,
        qualityTag: a.dataset.qualityTag,
      });
    });
  });
}

// ============================================================
// RECURSIVE SEARCH
// ============================================================
const searchPanel    = document.getElementById('searchPanel');
const searchResults  = document.getElementById('searchResults');
const searchStatus   = document.getElementById('searchStatus');
const searchStatusTx = searchStatus.querySelector('.search-status-text');
const searchTrunc    = document.getElementById('searchTruncated');
const filesListEl    = document.getElementById('fileList');

let searchDebounceTimer = null;
let searchAbortController = null;
let searchIsActive = false;

const SEARCH_DEBOUNCE_MS = 250;

const ICON_FALLBACK_FOLDER =
  '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>';
const ICON_FALLBACK_FILE =
  '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>';

function setSearchLoading(loading) {
  searchStatus.classList.toggle('loading', loading);
}

function showSearchPanel() {
  searchPanel.classList.add('active');
  filesListEl.style.display = 'none';
  searchIsActive = true;
}

function hideSearchPanel() {
  searchPanel.classList.remove('active');
  filesListEl.style.display = '';
  searchResults.innerHTML = '';
  searchTrunc.style.display = 'none';
  searchIsActive = false;
}

function buildSearchResultItem(item) {
  const li = document.createElement('li');
  li.dataset.name = item.name.toLowerCase();
  li.dataset.fullpath = item.path.toLowerCase();

  const a = document.createElement('a');
  a.href = item.url;
  a.className = item.is_dir ? 'nav-link' : 'file-row';

  if (!item.is_dir) {
    a.dataset.url = item.url;
    a.dataset.name = item.name;
    a.dataset.kind = item.kind || '';
    a.dataset.size = item.size || '';
    a.dataset.quality = item.quality || '';
    a.dataset.qualityTag = item.quality_tag || '';
    if (!item.kind) a.setAttribute('download', '');
  }

  const svg = item.svg || (item.is_dir ? ICON_FALLBACK_FOLDER : ICON_FALLBACK_FILE);
  const color = item.color || 'var(--muted)';

  let iconEl;
  if (item.thumb) {
    iconEl = document.createElement('div');
    iconEl.className = 'thumb';
    const img = document.createElement('img');
    img.src = item.thumb;
    img.alt = '';
    img.loading = 'lazy';
    img.decoding = 'async';
    iconEl.appendChild(img);
  } else {
    iconEl = document.createElement('div');
    iconEl.className = 'icon';
    iconEl.style.color = color;
    iconEl.innerHTML = '<svg viewBox="0 0 24 24">' + svg + '</svg>';
  }

  const infoDiv = document.createElement('div');
  infoDiv.className = 'info';

  const nameDiv = document.createElement('div');
  nameDiv.className = 'name';
  nameDiv.textContent = item.name + (item.is_dir ? '/' : '');

  const metaDiv = document.createElement('div');
  metaDiv.className = 'meta';

  if (!item.is_dir && item.size) {
    const s = document.createElement('span');
    s.textContent = item.size;
    metaDiv.appendChild(s);
  }
  if (item.mtime) {
    const s = document.createElement('span');
    s.textContent = item.mtime;
    metaDiv.appendChild(s);
  }
  if (item.quality) {
    const s = document.createElement('span');
    s.className = 'quality-badge';
    s.textContent = item.quality;
    if (item.quality_tag) {
      const t = document.createElement('span');
      t.className = 'quality-tag';
      t.textContent = item.quality_tag;
      s.appendChild(t);
    }
    metaDiv.appendChild(s);
  }

  const pathDiv = document.createElement('div');
  pathDiv.className = 'search-path';
  const parentPath = item.path.includes('/')
    ? '/' + item.path.split('/').slice(0, -1).join('/')
    : '/';
  pathDiv.textContent = parentPath;
  pathDiv.title = '/' + item.path;
  metaDiv.appendChild(pathDiv);

  infoDiv.appendChild(nameDiv);
  infoDiv.appendChild(metaDiv);

  const arrowDiv = document.createElement('div');
  arrowDiv.className = 'arrow';
  if (item.is_dir) {
    arrowDiv.innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>';
  } else if (item.kind) {
    arrowDiv.innerHTML = '<svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
  } else {
    arrowDiv.innerHTML = '<svg class="dl" viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/></svg>';
  }

  a.appendChild(iconEl);
  a.appendChild(infoDiv);
  a.appendChild(arrowDiv);
  li.appendChild(a);

  return li;
}

async function performSearch(query) {
  if (!query) {
    hideSearchPanel();
    return;
  }

  if (searchAbortController) {
    try { searchAbortController.abort(); } catch(e){}
  }
  searchAbortController = new AbortController();

  showSearchPanel();
  setSearchLoading(true);
  searchStatusTx.textContent = 'Searching for "' + query + '"…';
  searchTrunc.style.display = 'none';
  searchResults.innerHTML = '';

  try {
    const res = await fetch(
      '/api/search?q=' + encodeURIComponent(query),
      { signal: searchAbortController.signal, cache: 'no-store' }
    );

    if (!res.ok) {
      searchStatusTx.textContent = 'Search failed.';
      setSearchLoading(false);
      return;
    }

    const data = await res.json();
    const results = data.results || [];

    searchResults.innerHTML = '';

    if (results.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'search-empty';
      empty.textContent = 'No results for "' + query + '"';
      searchResults.appendChild(empty);
    } else {
      const frag = document.createDocumentFragment();
      results.forEach(item => frag.appendChild(buildSearchResultItem(item)));
      searchResults.appendChild(frag);
    }

    setSearchLoading(false);
    searchStatusTx.textContent =
      results.length + ' result' + (results.length === 1 ? '' : 's') + ' for "' + query + '"';

    if (data.truncated) {
      searchTrunc.textContent =
        'Showing first ' + results.length + ' results. Refine your search for more.';
      searchTrunc.style.display = '';
    }

    bindNavLinks();
    bindFileRows();
  } catch (err) {
    if (err.name === 'AbortError') return;
    setSearchLoading(false);
    searchStatusTx.textContent = 'Search error.';
  }
}

function rebindSearch() {
  const s = document.getElementById('search');
  if (!s) return;
  if (s.dataset.bound === '1') return;
  s.dataset.bound = '1';

  s.addEventListener('input', (e) => {
    const q = e.target.value.trim();
    clearTimeout(searchDebounceTimer);

    if (!q) {
      hideSearchPanel();
      return;
    }

    searchDebounceTimer = setTimeout(() => {
      performSearch(q);
    }, SEARCH_DEBOUNCE_MS);
  });

  s.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      s.value = '';
      hideSearchPanel();
      s.blur();
    }
  });
}

window.addEventListener('popstate', (e) => {
  if (handleFsGuardPop()) return;

  if (e.state && e.state.url) {
    navigateTo(e.state.url, false);
  } else {
    navigateTo(location.pathname + location.search, false);
  }
});

if (!history.state) {
  history.replaceState(
    { url: location.pathname + location.search },
    '',
    location.href
  );
}

bindNavLinks();
bindFileRows();
rebindSearch();

// ============================================================
// SILENT FILE LIST REFRESH
// ============================================================
let refreshInProgress = false;
let lastRefreshAt = 0;
const REFRESH_MIN_GAP = 800;

async function refreshFileList(opts = {}) {
  if (refreshInProgress) return;
  if (navInProgress) return;
  if (viewer.classList.contains('open')) return;
  if (searchIsActive) return;

  const searchEl = document.getElementById('search');
  if (searchEl && document.activeElement === searchEl) return;

  const now = Date.now();
  if (now - lastRefreshAt < REFRESH_MIN_GAP) return;
  lastRefreshAt = now;
  refreshInProgress = true;

  try {
    const target = withHiddenParam(location.pathname + location.search);
    const res = await fetch(target, {
      headers: { 'X-Requested-With': 'spa-nav' },
      cache: 'no-store',
    });
    if (!res.ok) return;

    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');

    const newList = doc.getElementById('fileList');
    const oldList = document.getElementById('fileList');
    if (newList && oldList) oldList.replaceWith(newList);

    const newHeader = doc.querySelector('header');
    const oldHeader = document.querySelector('header');
    if (newHeader && oldHeader) oldHeader.replaceWith(newHeader);

    const newStat = doc.querySelector('.stat');
    const oldStat = document.querySelector('.stat');
    if (newStat && oldStat) oldStat.replaceWith(newStat);

    const newEmpty = doc.querySelector('.empty');
    const oldEmpty = document.querySelector('.empty');
    if (newEmpty && oldEmpty) {
      oldEmpty.replaceWith(newEmpty);
    } else if (newEmpty && !oldEmpty) {
      const listParent = document.getElementById('fileList')?.parentNode;
      if (listParent) listParent.appendChild(newEmpty);
    } else if (!newEmpty && oldEmpty) {
      oldEmpty.remove();
    }

    bindNavLinks();
    bindFileRows();
    rebindSearch();
    bindViewToggle();
  } catch (err) {
    // silent
  } finally {
    refreshInProgress = false;
  }
}

// ============================================================
// SSE — real-time updates
// ============================================================
let sseSource = null;
let sseReconnectTimer = null;
let sseReconnectDelay = 1000;
const SSE_MAX_DELAY = 30000;

let refreshDebounceTimer = null;
const REFRESH_DEBOUNCE_MS = 300;

function scheduleRefresh() {
  clearTimeout(refreshDebounceTimer);
  refreshDebounceTimer = setTimeout(() => {
    refreshFileList();
  }, REFRESH_DEBOUNCE_MS);
}

function connectSSE() {
  if (sseSource) {
    try { sseSource.close(); } catch(e){}
    sseSource = null;
  }
  clearTimeout(sseReconnectTimer);

  try {
    sseSource = new EventSource('/events');
  } catch (e) {
    scheduleReconnect();
    return;
  }

  sseSource.addEventListener('open', () => {
    sseReconnectDelay = 1000;
  });

  sseSource.addEventListener('changed', () => {
    scheduleRefresh();
  });

  sseSource.addEventListener('error', () => {
    try { sseSource.close(); } catch(e){}
    sseSource = null;
    scheduleReconnect();
  });
}

function scheduleReconnect() {
  clearTimeout(sseReconnectTimer);
  sseReconnectTimer = setTimeout(() => {
    sseReconnectDelay = Math.min(sseReconnectDelay * 1.5, SSE_MAX_DELAY);
    connectSSE();
  }, sseReconnectDelay);
}

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    if (!sseSource || sseSource.readyState === EventSource.CLOSED) {
      sseReconnectDelay = 1000;
      connectSSE();
    }
  }
});

document.addEventListener('keydown', (e) => {
  const tag = (e.target.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'textarea') return;
  if (viewer.classList.contains('open')) return;

  if (e.key === 'r' || e.key === 'R') {
    e.preventDefault();
    refreshFileList();
  }
});

connectSSE();

// ============================================================
// VIDEO PLAYER
// ============================================================
function buildVideoPlayer(src, name, quality, qualityTag) {
  const wrap = document.createElement('div');
  wrap.className = 'video-wrap';

  const labelText = quality || '—';
  const tagText = qualityTag || '';

  wrap.innerHTML = `
    <video playsinline webkit-playsinline preload="auto" src="${src}"></video>
    <div class="v-loading"></div>
    <div class="v-error">
      <svg viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 8v5M12 16h.01"/>
      </svg>
      <div class="v-error-title">Cannot play this file</div>
      <div class="v-error-msg">Your browser may not support this format or codec. Try downloading it or use another player.</div>
    </div>
    <button class="v-bigplay show" aria-label="Play">
      <svg viewBox="0 0 24 24"><path d="M9 5.5v13l11-6.5z"/></svg>
    </button>
    <div class="v-seek-indicator left">
      <svg viewBox="0 0 24 24"><path d="M11 19l-9-7 9-7v14zM22 19l-9-7 9-7v14z"/></svg>
      <span class="v-seek-text"></span>
    </div>
    <div class="v-seek-indicator right">
      <svg viewBox="0 0 24 24"><path d="M13 5l9 7-9 7V5zM2 5l9 7-9 7V5z"/></svg>
      <span class="v-seek-text"></span>
    </div>
    <div class="v-menu v-speed-menu">
      ${[0.5,0.75,1,1.25,1.5,2].map(s =>
        `<button data-speed="${s}" class="${s===1?'active':''}">${s}x</button>`).join('')}
    </div>
    <div class="v-menu v-picture-menu">
      <div class="v-picture-row">
        <label>Contrast <span data-val="contrast">110%</span></label>
        <input type="range" min="0.7" max="1.5" step="0.01" data-filter="contrast">
      </div>
      <div class="v-picture-row">
        <label>Saturation <span data-val="saturate">115%</span></label>
        <input type="range" min="0" max="2" step="0.01" data-filter="saturate">
      </div>
      <div class="v-picture-row">
        <label>Brightness <span data-val="brightness">100%</span></label>
        <input type="range" min="0.7" max="1.4" step="0.01" data-filter="brightness">
      </div>
      <div class="v-picture-row">
        <label>Warmth <span data-val="sepia">0%</span></label>
        <input type="range" min="0" max="0.3" step="0.01" data-filter="sepia">
      </div>
      <button class="v-picture-reset" type="button">Reset</button>
    </div>
    <div class="v-preset-overlay">
      <div class="v-preset-panel">
        <div class="v-preset-title">
          <span>Picture Presets</span>
          <button class="v-preset-close" title="Close" type="button">
            <svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="v-preset-grid"></div>
      </div>
    </div>
    <div class="v-ctrl">
      <div class="v-progress">
        <div class="v-progress-track">
          <div class="v-buffered"></div>
          <div class="v-played"></div>
        </div>
        <div class="v-thumb"></div>
        <div class="v-time-tooltip">0:00</div>
      </div>
      <div class="v-row">
        <button class="v-play" title="Play / Pause (Space)">
          <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <button class="v-skip v-back v-hide-narrow" title="Back 10s">
          <svg viewBox="0 0 24 24"><path d="M11 19l-9-7 9-7v14zM22 19l-9-7 9-7v14z"/></svg>
        </button>
        <button class="v-skip v-fwd v-hide-narrow" title="Forward 10s">
          <svg viewBox="0 0 24 24"><path d="M13 5l9 7-9 7V5zM2 5l9 7-9 7V5z"/></svg>
        </button>
        <span class="v-time" data-role="time">0:00 / 0:00</span>
        <div class="v-spacer"></div>
        <div class="v-volume">
          <button class="v-mute" title="Mute (M)">
            <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
          </button>
          <div class="v-volume-slider">
            <input type="range" min="0" max="1" step="0.01" value="1">
          </div>
        </div>
        <button class="v-quality v-hide-mobile" tabindex="-1" aria-disabled="true">
          <svg viewBox="0 0 24 24">
            <path d="M4 6h16M4 12h16M4 18h16"/>
            <circle cx="8" cy="6" r="2"/>
            <circle cx="16" cy="12" r="2"/>
            <circle cx="10" cy="18" r="2"/>
          </svg>
          <span class="v-quality-label">${labelText}</span>
          ${tagText ? `<span class="v-quality-tag">${tagText}</span>` : ''}
        </button>
        <button class="v-picture v-hide-mobile" title="Picture settings (C to cycle)">
          <svg viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/>
          </svg>
        </button>
        <button class="v-preset-btn v-hide-mobile" title="Presets (P)">
          <svg viewBox="0 0 24 24">
            <path d="M4 6h16M4 12h16M4 18h16"/>
            <circle cx="9" cy="6" r="2" fill="currentColor"/>
            <circle cx="15" cy="12" r="2" fill="currentColor"/>
            <circle cx="7" cy="18" r="2" fill="currentColor"/>
          </svg>
          <span class="v-preset-btn-label">Presets</span>
        </button>
        <button class="v-speed" title="Playback speed">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
        </button>
        <button class="v-pip v-hide-mobile" title="Picture in Picture">
          <svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><rect x="12" y="12" width="8" height="6" rx="1"/></svg>
        </button>
        <button class="v-full v-hide-mobile" title="Fullscreen (F)">
          <svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
        </button>
      </div>
    </div>
  `;

  const video       = wrap.querySelector('video');
  const loading     = wrap.querySelector('.v-loading');
  const errorBox    = wrap.querySelector('.v-error');
  const bigPlay     = wrap.querySelector('.v-bigplay');
  const played      = wrap.querySelector('.v-played');
  const buffered    = wrap.querySelector('.v-buffered');
  const prog        = wrap.querySelector('.v-progress');
  const thumb       = wrap.querySelector('.v-thumb');
  const tooltip     = wrap.querySelector('.v-time-tooltip');
  const timeEl      = wrap.querySelector('[data-role=time]');
  const btnPlay     = wrap.querySelector('.v-play');
  const btnBack     = wrap.querySelector('.v-back');
  const btnFwd      = wrap.querySelector('.v-fwd');
  const btnMute     = wrap.querySelector('.v-mute');
  const volIn       = wrap.querySelector('.v-volume-slider input');
  const btnSpeed    = wrap.querySelector('.v-speed');
  const speedMenu   = wrap.querySelector('.v-speed-menu');
  const btnPicture  = wrap.querySelector('.v-picture');
  const pictureMenu = wrap.querySelector('.v-picture-menu');
  const btnPreset   = wrap.querySelector('.v-preset-btn');
  const presetOverlay = wrap.querySelector('.v-preset-overlay');
  const presetGrid    = wrap.querySelector('.v-preset-grid');
  const presetClose   = wrap.querySelector('.v-preset-close');
  const btnPip      = wrap.querySelector('.v-pip');
  const btnFull     = wrap.querySelector('.v-full');
  const indLeft     = wrap.querySelector('.v-seek-indicator.left');
  const indRight    = wrap.querySelector('.v-seek-indicator.right');
  const seekLeft    = indLeft.querySelector('.v-seek-text');
  const seekRight   = indRight.querySelector('.v-seek-text');

  const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
  const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';

  function fmt(t){
    if (!isFinite(t) || t < 0) return '0:00';
    const h = Math.floor(t/3600), m = Math.floor((t%3600)/60), s = Math.floor(t%60);
    return (h ? h+':'+String(m).padStart(2,'0') : m) + ':' + String(s).padStart(2,'0');
  }
  function safeDuration(){
    return isFinite(video.duration) && video.duration > 0 ? video.duration : 0;
  }
  function updateTime(){
    timeEl.textContent = fmt(video.currentTime) + ' / ' + fmt(safeDuration());
  }
  function updateProgress(){
    const d = safeDuration();
    const p = d ? (video.currentTime / d) * 100 : 0;
    played.style.width = p + '%';
    thumb.style.left = p + '%';
    try {
      if (video.buffered.length && d) {
        const b = video.buffered.end(video.buffered.length - 1);
        buffered.style.width = Math.min(100, (b / d) * 100) + '%';
      }
    } catch(e) {}
  }
  function playPause(){
    if (video.paused) {
      const p = video.play();
      if (p && p.catch) {
        p.catch(err => {
          console.warn('Playback failed:', err);
          loading.classList.remove('show');
          bigPlay.classList.add('show');
          errorBox.classList.add('show');
        });
      }
    } else {
      video.pause();
    }
  }

  const pictureSettings = loadPictureSettings();
  applyPictureTo(video, pictureSettings);

  const pictureInputs = pictureMenu.querySelectorAll('input[data-filter]');
  function refreshPictureUI(){
    pictureInputs.forEach(inp => {
      const key = inp.dataset.filter;
      const v = pictureSettings[key];
      inp.value = v;
      const valEl = pictureMenu.querySelector(`[data-val="${key}"]`);
      if (valEl) valEl.textContent = Math.round(v * 100) + '%';
    });
  }
  pictureInputs.forEach(inp => {
    const key = inp.dataset.filter;
    inp.value = pictureSettings[key];
    const valEl = pictureMenu.querySelector(`[data-val="${key}"]`);
    if (valEl) valEl.textContent = Math.round(pictureSettings[key] * 100) + '%';
    inp.addEventListener('input', () => {
      const v = parseFloat(inp.value);
      pictureSettings[key] = v;
      applyPictureTo(video, pictureSettings);
      savePictureSettings(pictureSettings);
      if (valEl) valEl.textContent = Math.round(v * 100) + '%';
      refreshPresetActive();
    });
  });
  const resetBtn = pictureMenu.querySelector('.v-picture-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      Object.assign(pictureSettings, DEFAULT_PICTURE);
      applyPictureTo(video, pictureSettings);
      savePictureSettings(pictureSettings);
      refreshPictureUI();
      refreshPresetActive();
    });
  }
  function onPictureClick(e){
    e.stopPropagation();
    speedMenu.classList.remove('show');
    pictureMenu.classList.toggle('show');
  }
  if (btnPicture) btnPicture.addEventListener('click', onPictureClick);

  function buildPresetGrid(){
    presetGrid.innerHTML = '';
    PICTURE_PRESET_LIST.forEach(p => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'v-preset-item';
      btn.dataset.preset = p.key;
      btn.innerHTML = `
        <span class="v-preset-name">${p.name}</span>
        <span class="v-preset-desc">${p.desc}</span>
        <span class="v-preset-swatch"></span>
      `;
      btn.addEventListener('click', () => {
        Object.assign(pictureSettings, p.values);
        applyPictureTo(video, pictureSettings);
        savePictureSettings(pictureSettings);
        refreshPictureUI();
        refreshPresetActive();
        showPlayerToast('Preset: ' + p.name, false);
        setTimeout(closePresetOverlay, 250);
      });
      presetGrid.appendChild(btn);
    });
    refreshPresetActive();
  }

  function refreshPresetActive(){
    const match = PICTURE_PRESET_LIST.find(p =>
      p.values.contrast.toFixed(2) === pictureSettings.contrast.toFixed(2) &&
      p.values.saturate.toFixed(2) === pictureSettings.saturate.toFixed(2) &&
      p.values.brightness.toFixed(2) === pictureSettings.brightness.toFixed(2) &&
      p.values.sepia.toFixed(2) === (pictureSettings.sepia || 0).toFixed(2)
    );
    presetGrid.querySelectorAll('.v-preset-item').forEach(el => {
      el.classList.toggle('active', !!match && el.dataset.preset === match.key);
    });
  }

  function openPresetOverlay(){
    speedMenu.classList.remove('show');
    pictureMenu.classList.remove('show');
    presetOverlay.classList.add('show');
    refreshPresetActive();
  }
  function closePresetOverlay(){
    presetOverlay.classList.remove('show');
  }

  if (btnPreset) {
    btnPreset.addEventListener('click', (e) => {
      e.stopPropagation();
      openPresetOverlay();
    });
  }
  if (presetClose) {
    presetClose.addEventListener('click', (e) => {
      e.stopPropagation();
      closePresetOverlay();
    });
  }
  presetOverlay.addEventListener('click', (e) => {
    if (e.target === presetOverlay) closePresetOverlay();
  });

  function onPresetEsc(e){
    if (e.key === 'Escape' && presetOverlay.classList.contains('show')) {
      e.stopPropagation();
      closePresetOverlay();
    }
  }
  document.addEventListener('keydown', onPresetEsc);

  buildPresetGrid();

  function showPlayerToast(html, withRestart) {
    const toast = document.createElement('div');
    toast.className = 'v-resume-toast';
    toast.innerHTML = `
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;">
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>
      </svg>
      <span>${html}</span>
    `;
    if (withRestart) {
      const btn = document.createElement('button');
      btn.className = 'v-resume-restart';
      btn.type = 'button';
      btn.textContent = 'Start over';
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearTimeout(hideTimer);
        video.currentTime = 0;
        clearResumeTime(src);
        remove();
      });
      toast.appendChild(btn);
    }
    wrap.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    const remove = () => {
      toast.classList.remove('show');
      setTimeout(() => { try { toast.remove(); } catch(e){} }, 300);
    };
    const hideTimer = setTimeout(remove, 4000);
    const onInteract = () => { clearTimeout(hideTimer); remove(); };
    wrap.addEventListener('pointerdown', onInteract, { once: true });
  }

  function onPlay(){ btnPlay.innerHTML = ICON_PAUSE; bigPlay.classList.remove('show'); }
  function onPause(){
    btnPlay.innerHTML = ICON_PLAY;
    bigPlay.classList.add('show');
    saveResumeTime(src, video.currentTime, video.duration);
  }
  function onEnded(){
    btnPlay.innerHTML = ICON_PLAY;
    bigPlay.classList.add('show');
    clearResumeTime(src);
  }
  function onTimeUpdate(){ updateTime(); updateProgress(); saveResume(); }
  function onProgressBar(){ updateProgress(); }
  function onLoadedMeta(){
    updateTime();
    const saved = loadResumeTime(src);
    const dur = safeDuration();
    if (saved > 2 && (!dur || saved < dur - 5)) {
      video.currentTime = saved;
      showPlayerToast('Resumed at ' + fmt(saved), true);
    }
  }
  function onWaiting(){ loading.classList.add('show'); }
  function onPlaying(){ loading.classList.remove('show'); errorBox.classList.remove('show'); }
  function onCanPlay(){ loading.classList.remove('show'); }
  function onVideoError(){
    loading.classList.remove('show');
    bigPlay.classList.remove('show');
    errorBox.classList.add('show');
  }
  function onVideoClick(e){ if (e.target === video) playPause(); }

  let resumeSaveTimer = null;
  function saveResume(){
    clearTimeout(resumeSaveTimer);
    resumeSaveTimer = setTimeout(() => {
      if (!video.paused) saveResumeTime(src, video.currentTime, video.duration);
    }, 1000);
  }

  video.addEventListener('play', onPlay);
  video.addEventListener('pause', onPause);
  video.addEventListener('ended', onEnded);
  video.addEventListener('timeupdate', onTimeUpdate);
  video.addEventListener('progress', onProgressBar);
  video.addEventListener('loadedmetadata', onLoadedMeta);
  video.addEventListener('waiting', onWaiting);
  video.addEventListener('playing', onPlaying);
  video.addEventListener('canplay', onCanPlay);
  video.addEventListener('error', onVideoError);
  video.addEventListener('click', onVideoClick);

  bigPlay.addEventListener('click', playPause);
  btnPlay.addEventListener('click', playPause);

  function onBack(){ video.currentTime = Math.max(0, video.currentTime - 10); }
  function onFwd(){
    const d = safeDuration();
    video.currentTime = d ? Math.min(d, video.currentTime + 10) : video.currentTime + 10;
  }
  if (btnBack) btnBack.addEventListener('click', onBack);
  if (btnFwd)  btnFwd .addEventListener('click', onFwd);

  let seeking = false;

  function timeFromEvent(e){
    const rect = prog.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const ratio = Math.max(0, Math.min(1, x / rect.width));
    return { ratio, time: ratio * safeDuration() };
  }
  function seekFromEvent(e){
    const d = safeDuration();
    if (!d) return;
    video.currentTime = timeFromEvent(e).time;
  }
  function onProgDown(e){ seeking = true; seekFromEvent(e); }
  function onWinMove(e){ if (seeking) seekFromEvent(e); }
  function onWinUp(){ seeking = false; }
  function onProgTouch(e){ seekFromEvent(e); }

  function onProgMove(e){
    if (seeking || !safeDuration()) return;
    const { ratio, time } = timeFromEvent(e);
    tooltip.textContent = fmt(time);
    tooltip.style.left = (ratio * 100) + '%';
    tooltip.classList.add('show');
  }
  function onProgLeave(){ tooltip.classList.remove('show'); }

  function onProgTouchMove(e){
    if (!safeDuration()) return;
    const { ratio, time } = timeFromEvent(e);
    tooltip.textContent = fmt(time);
    tooltip.style.left = (ratio * 100) + '%';
    tooltip.classList.add('show');
  }
  function onProgTouchEnd(){ tooltip.classList.remove('show'); }

  prog.addEventListener('mousedown', onProgDown);
  window.addEventListener('mousemove', onWinMove);
  window.addEventListener('mouseup', onWinUp);
  prog.addEventListener('mousemove', onProgMove);
  prog.addEventListener('mouseleave', onProgLeave);
  prog.addEventListener('touchstart', onProgTouch, { passive: true });
  prog.addEventListener('touchmove', (e) => {
    onProgTouch(e);
    onProgTouchMove(e);
  }, { passive: true });
  prog.addEventListener('touchend', onProgTouchEnd);

  function updateMuteIcon(){
    btnMute.innerHTML = (video.muted || video.volume === 0)
      ? '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M22 9l-6 6M16 9l6 6"/></svg>'
      : '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
  }
  function onMuteClick(){
    video.muted = !video.muted;
    volIn.value = video.muted ? 0 : video.volume;
    updateMuteIcon();
  }
  function onVolInput(){
    video.volume = parseFloat(volIn.value);
    video.muted = video.volume === 0;
    updateMuteIcon();
  }
  btnMute.addEventListener('click', onMuteClick);
  volIn.addEventListener('input', onVolInput);

  function onSpeedClick(e){ e.stopPropagation(); pictureMenu.classList.remove('show'); speedMenu.classList.toggle('show'); }
  btnSpeed.addEventListener('click', onSpeedClick);
  const speedButtons = Array.from(speedMenu.querySelectorAll('button'));
  function onSpeedBtnClick(e){
    const b = e.currentTarget;
    video.playbackRate = parseFloat(b.dataset.speed);
    speedButtons.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    speedMenu.classList.remove('show');
  }
  speedButtons.forEach(b => b.addEventListener('click', onSpeedBtnClick));

  let idleTimer = null;
  function wake(){
    wrap.classList.remove('idle');
    wrap.classList.remove('hide-cursor');
    clearTimeout(idleTimer);
    if (!video.paused && !presetOverlay.classList.contains('show')) {
      idleTimer = setTimeout(() => {
        wrap.classList.add('idle');
        wrap.classList.add('hide-cursor');
        speedMenu.classList.remove('show');
        pictureMenu.classList.remove('show');
      }, 3000);
    }
  }
  function onVideoPauseClear(){
    clearTimeout(idleTimer);
    wrap.classList.remove('idle');
    wrap.classList.remove('hide-cursor');
  }
  wrap.addEventListener('mousemove', wake);
  wrap.addEventListener('mousedown', wake);
  wrap.addEventListener('touchstart', wake, { passive: true });
  wrap.addEventListener('touchmove', wake, { passive: true });
  video.addEventListener('play', wake);
  video.addEventListener('pause', onVideoPauseClear);
  speedMenu.addEventListener('mousemove', wake);
  pictureMenu.addEventListener('mousemove', wake);

  function onDocClick(){ speedMenu.classList.remove('show'); pictureMenu.classList.remove('show'); }
  document.addEventListener('click', onDocClick);
  function onWrapClick(e){ e.stopPropagation(); }
  wrap.addEventListener('click', onWrapClick);

  async function onPipClick(){
    try {
      if (document.pictureInPictureElement) await document.exitPictureInPicture();
      else if (video.requestPictureInPicture) await video.requestPictureInPicture();
    } catch(e){}
  }
  if (btnPip) btnPip.addEventListener('click', onPipClick);

  function onFullClick(){
    if (isFS()) exitFS();
    else requestFS(wrap);
  }
  if (btnFull) btnFull.addEventListener('click', onFullClick);

  function cyclePicturePreset(){
    const CORE = PICTURE_PRESET_LIST.slice(0, 5);
    const currentContrast = pictureSettings.contrast.toFixed(2);
    let idx = CORE.findIndex(p => p.values.contrast.toFixed(2) === currentContrast);
    idx = (idx + 1) % CORE.length;
    Object.assign(pictureSettings, CORE[idx].values);
    applyPictureTo(video, pictureSettings);
    savePictureSettings(pictureSettings);
    refreshPictureUI();
    refreshPresetActive();
    showPlayerToast('Picture: ' + CORE[idx].name, false);
  }

  function onWrapKeydown(e){
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;

    if (presetOverlay.classList.contains('show') && e.key !== 'Escape') {
      return;
    }

    wake();
    if (e.key === ' ' || e.key === 'k' || e.key === 'K') {
      e.preventDefault();
      playPause();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      const d = safeDuration();
      video.currentTime = d ? Math.min(d, video.currentTime + 5) : video.currentTime + 5;
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      video.currentTime = Math.max(0, video.currentTime - 5);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      video.volume = Math.min(1, video.volume + 0.05);
      volIn.value = video.volume;
      video.muted = false;
      updateMuteIcon();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      video.volume = Math.max(0, video.volume - 0.05);
      volIn.value = video.volume;
      updateMuteIcon();
    } else if (e.key === 'm' || e.key === 'M') {
      video.muted = !video.muted;
      updateMuteIcon();
    } else if (e.key === 'f' || e.key === 'F') {
      if (isFS()) exitFS(); else requestFS(wrap);
    } else if (e.key === 'c' || e.key === 'C') {
      cyclePicturePreset();
    } else if (e.key === 'p' || e.key === 'P') {
      e.preventDefault();
      if (presetOverlay.classList.contains('show')) closePresetOverlay();
      else openPresetOverlay();
    }
  }
  wrap.tabIndex = 0;
  wrap.addEventListener('keydown', onWrapKeydown);

  let lastTapTime = 0;
  let tapTimer = null;
  let tapSide = null;
  let tapCount = 0;

  function triggerSeekIndicator(side){
    const el = side === 'left' ? indLeft : indRight;
    const txt = side === 'left' ? seekLeft : seekRight;
    el.classList.add('show');
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => el.classList.remove('show'), 700);
    return txt;
  }

  function onVideoTouchStart(e){
    const now = Date.now();
    const touch = e.touches[0];
    const rect = video.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const side = x < rect.width / 2 ? 'left' : 'right';

    if (now - lastTapTime < 300 && side === tapSide) {
      tapCount++;
      const step = 10;
      if (side === 'left') {
        video.currentTime = Math.max(0, video.currentTime - step);
      } else {
        const d = safeDuration();
        video.currentTime = d ? Math.min(d, video.currentTime + step) : video.currentTime + step;
      }
      const txt = triggerSeekIndicator(side);
      txt.textContent = (side === 'left' ? '−' : '+') + (step * tapCount) + 's';
      clearTimeout(tapTimer);
      tapTimer = setTimeout(() => { tapCount = 0; }, 800);
    } else {
      clearTimeout(tapTimer);
      tapCount = 0;
      tapTimer = setTimeout(() => {
        if (tapCount === 0) playPause();
      }, 280);
    }
    lastTapTime = now;
    tapSide = side;
  }
  video.addEventListener('touchstart', onVideoTouchStart, { passive: true });

  try {
    if ('mediaSession' in navigator && window.MediaMetadata) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: name || 'Video',
        artist: 'Shared Files',
      });
      navigator.mediaSession.setActionHandler('play', () => video.play());
      navigator.mediaSession.setActionHandler('pause', () => video.pause());
      navigator.mediaSession.setActionHandler('seekbackward', () => {
        video.currentTime = Math.max(0, video.currentTime - 10);
      });
      navigator.mediaSession.setActionHandler('seekforward', () => {
        const d = safeDuration();
        video.currentTime = d ? Math.min(d, video.currentTime + 10) : video.currentTime + 10;
      });
    }
  } catch(e){}

  function onVisibilityChange(){
    if (document.hidden) {
      saveResumeTime(src, video.currentTime, video.duration);
      if (!video.paused) video.pause();
    }
  }
  document.addEventListener('visibilitychange', onVisibilityChange);

  function onBeforeUnload(){
    saveResumeTime(src, video.currentTime, video.duration);
  }
  window.addEventListener('beforeunload', onBeforeUnload);
  window.addEventListener('pagehide', onBeforeUnload);

  updateMuteIcon();
  refreshPictureUI();
  setTimeout(() => wrap.focus(), 100);
  wake();

  function cleanup(){
    if (video && video.currentTime > 0) {
      saveResumeTime(src, video.currentTime, video.duration);
    }
    clearTimeout(idleTimer);
    clearTimeout(resumeSaveTimer);
    clearTimeout(tapTimer);
    clearTimeout(indLeft._hideTimer);
    clearTimeout(indRight._hideTimer);
    window.removeEventListener('mousemove', onWinMove);
    window.removeEventListener('mouseup', onWinUp);
    window.removeEventListener('beforeunload', onBeforeUnload);
    window.removeEventListener('pagehide', onBeforeUnload);
    document.removeEventListener('click', onDocClick);
    document.removeEventListener('visibilitychange', onVisibilityChange);
    document.removeEventListener('keydown', onPresetEsc);
    try {
      if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', null);
        navigator.mediaSession.setActionHandler('pause', null);
        navigator.mediaSession.setActionHandler('seekbackward', null);
        navigator.mediaSession.setActionHandler('seekforward', null);
        navigator.mediaSession.metadata = null;
      }
    } catch(e){}
  }

  return { el: wrap, cleanup };
}

// ============================================================
// AUDIO PLAYER
// ============================================================
function buildAudioPlayer(src, name) {
  const card = document.createElement('div');
  card.className = 'audio-card';

  card.innerHTML = `
    <div class="audio-head">
      <div class="a-icon">
        <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
      </div>
      <div class="a-name"></div>
    </div>
    <div class="video-wrap" style="height:auto; background:transparent; border-radius:0; position:relative;">
      <audio src="${src}" preload="auto"></audio>
      <div class="v-menu v-speed-menu">
        ${[0.5,0.75,1,1.25,1.5,2].map(s =>
          `<button data-speed="${s}" class="${s===1?'active':''}">${s}x</button>`).join('')}
      </div>
      <div class="v-ctrl" style="position:static;">
        <div class="v-progress">
          <div class="v-progress-track">
            <div class="v-buffered"></div>
            <div class="v-played"></div>
          </div>
          <div class="v-thumb"></div>
          <div class="v-time-tooltip">0:00</div>
        </div>
        <div class="v-row">
          <button class="v-play" title="Play / Pause (Space)">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
          <span class="v-time" data-role="time">0:00 / 0:00</span>
          <div class="v-spacer"></div>
          <div class="v-volume">
            <button class="v-mute" title="Mute (M)">
              <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            </button>
            <div class="v-volume-slider">
              <input type="range" min="0" max="1" step="0.01" value="1">
            </div>
          </div>
          <button class="v-speed" title="Playback speed">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
          </button>
        </div>
      </div>
    </div>
  `;
  card.querySelector('.a-name').textContent = name;

  const audio     = card.querySelector('audio');
  const btnPlay   = card.querySelector('.v-play');
  const played    = card.querySelector('.v-played');
  const buffered  = card.querySelector('.v-buffered');
  const prog      = card.querySelector('.v-progress');
  const thumb     = card.querySelector('.v-thumb');
  const tooltip   = card.querySelector('.v-time-tooltip');
  const timeEl    = card.querySelector('[data-role=time]');
  const btnMute   = card.querySelector('.v-mute');
  const volIn     = card.querySelector('.v-volume-slider input');
  const btnSpeed  = card.querySelector('.v-speed');
  const menu      = card.querySelector('.v-speed-menu');

  const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
  const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';

  function fmt(t){
    if (!isFinite(t) || t < 0) return '0:00';
    const m = Math.floor(t/60), s = Math.floor(t%60);
    return m + ':' + String(s).padStart(2,'0');
  }
  function safeDuration(){
    return isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
  }
  function update(){
    timeEl.textContent = fmt(audio.currentTime) + ' / ' + fmt(safeDuration());
    const d = safeDuration();
    const p = d ? (audio.currentTime/d)*100 : 0;
    played.style.width = p + '%';
    thumb.style.left = p + '%';
    try {
      if (audio.buffered.length && d) {
        const b = audio.buffered.end(audio.buffered.length - 1);
        buffered.style.width = Math.min(100, (b/d)*100) + '%';
      }
    } catch(e){}
  }
  function playPause(){
    if (audio.paused) {
      const p = audio.play();
      if (p && p.catch) p.catch(err => console.warn('Audio playback failed:', err));
    } else {
      audio.pause();
    }
  }
  function onPlay(){ btnPlay.innerHTML = ICON_PAUSE; }
  function onPause(){
    btnPlay.innerHTML = ICON_PLAY;
    saveResumeTime(src, audio.currentTime, audio.duration);
  }
  function onEnded(){
    btnPlay.innerHTML = ICON_PLAY;
    clearResumeTime(src);
  }
  function onLoadedMeta(){
    update();
    const saved = loadResumeTime(src);
    const dur = safeDuration();
    if (saved > 2 && (!dur || saved < dur - 5)) {
      audio.currentTime = saved;
      showAudioToast('Resumed at ' + fmt(saved));
    }
  }
  function showAudioToast(html){
    const toast = document.createElement('div');
    toast.className = 'v-resume-toast';
    toast.innerHTML = `
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;">
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>
      </svg>
      <span>${html}</span>
    `;
    const btn = document.createElement('button');
    btn.className = 'v-resume-restart';
    btn.type = 'button';
    btn.textContent = 'Start over';
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearTimeout(hideTimer);
      audio.currentTime = 0;
      clearResumeTime(src);
      remove();
    });
    toast.appendChild(btn);
    card.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    const remove = () => {
      toast.classList.remove('show');
      setTimeout(() => { try { toast.remove(); } catch(e){} }, 300);
    };
    const hideTimer = setTimeout(remove, 4000);
  }

  audio.addEventListener('timeupdate', update);
  audio.addEventListener('loadedmetadata', onLoadedMeta);
  audio.addEventListener('play', onPlay);
  audio.addEventListener('pause', onPause);
  audio.addEventListener('ended', onEnded);
  btnPlay.addEventListener('click', playPause);

  let resumeSaveTimer = null;
  function saveResume(){
    clearTimeout(resumeSaveTimer);
    resumeSaveTimer = setTimeout(() => {
      if (!audio.paused) saveResumeTime(src, audio.currentTime, audio.duration);
    }, 1000);
  }
  audio.addEventListener('timeupdate', saveResume);

  let s = false;
  function timeFromEvent(e){
    const rect = prog.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const ratio = Math.max(0, Math.min(1, x/rect.width));
    return { ratio, time: ratio * safeDuration() };
  }
  function seekFromEvent(e){
    const d = safeDuration();
    if (!d) return;
    audio.currentTime = timeFromEvent(e).time;
  }
  function onDown(e){ s = true; seekFromEvent(e); }
  function onMove(e){ if (s) seekFromEvent(e); }
  function onUp(){ s = false; }
  function onTouch(e){ seekFromEvent(e); }
  function onProgMove(e){
    if (s || !safeDuration()) return;
    const { ratio, time } = timeFromEvent(e);
    tooltip.textContent = fmt(time);
    tooltip.style.left = (ratio * 100) + '%';
    tooltip.classList.add('show');
  }
  function onProgLeave(){ tooltip.classList.remove('show'); }

  prog.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  prog.addEventListener('mousemove', onProgMove);
  prog.addEventListener('mouseleave', onProgLeave);
  prog.addEventListener('touchstart', onTouch, { passive: true });
  prog.addEventListener('touchmove', onTouch, { passive: true });

  function updateMuteIcon(){
    btnMute.innerHTML = (audio.muted || audio.volume === 0)
      ? '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M22 9l-6 6M16 9l6 6"/></svg>'
      : '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
  }
  function onMuteClick(){ audio.muted = !audio.muted; updateMuteIcon(); }
  function onVolInput(){
    audio.volume = parseFloat(volIn.value);
    audio.muted = audio.volume === 0;
    updateMuteIcon();
  }
  btnMute.addEventListener('click', onMuteClick);
  volIn.addEventListener('input', onVolInput);

  function onSpeedClick(e){ e.stopPropagation(); menu.classList.toggle('show'); }
  btnSpeed.addEventListener('click', onSpeedClick);
  const speedButtons = Array.from(menu.querySelectorAll('button'));
  function onSpeedBtnClick(e){
    const b = e.currentTarget;
    audio.playbackRate = parseFloat(b.dataset.speed);
    speedButtons.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    menu.classList.remove('show');
  }
  speedButtons.forEach(b => b.addEventListener('click', onSpeedBtnClick));

  function onDocClick(){ menu.classList.remove('show'); }
  document.addEventListener('click', onDocClick);

  card.tabIndex = 0;
  card.style.outline = 'none';
  function onCardKeydown(e){
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;
    if (e.key === ' ' || e.key === 'k' || e.key === 'K') { e.preventDefault(); playPause(); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); audio.currentTime += 5; }
    else if (e.key === 'ArrowLeft')  { e.preventDefault(); audio.currentTime = Math.max(0, audio.currentTime - 5); }
    else if (e.key === 'ArrowUp')    { e.preventDefault(); audio.volume = Math.min(1, audio.volume + 0.05); volIn.value = audio.volume; updateMuteIcon(); }
    else if (e.key === 'ArrowDown')  { e.preventDefault(); audio.volume = Math.max(0, audio.volume - 0.05); volIn.value = audio.volume; updateMuteIcon(); }
    else if (e.key === 'm' || e.key === 'M') { audio.muted = !audio.muted; updateMuteIcon(); }
  }
  card.addEventListener('keydown', onCardKeydown);

  try {
    if ('mediaSession' in navigator && window.MediaMetadata) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: name || 'Audio',
        artist: 'Shared Files',
      });
      navigator.mediaSession.setActionHandler('play', () => audio.play());
      navigator.mediaSession.setActionHandler('pause', () => audio.pause());
      navigator.mediaSession.setActionHandler('seekbackward', () => {
        audio.currentTime = Math.max(0, audio.currentTime - 10);
      });
      navigator.mediaSession.setActionHandler('seekforward', () => {
        audio.currentTime += 10;
      });
    }
  } catch(e){}

  function onVisibilityChange(){
    if (document.hidden) {
      saveResumeTime(src, audio.currentTime, audio.duration);
      if (!audio.paused) audio.pause();
    }
  }
  document.addEventListener('visibilitychange', onVisibilityChange);

  function onBeforeUnload(){
    saveResumeTime(src, audio.currentTime, audio.duration);
  }
  window.addEventListener('beforeunload', onBeforeUnload);
  window.addEventListener('pagehide', onBeforeUnload);

  updateMuteIcon();

  function cleanup(){
    if (audio && audio.currentTime > 0) {
      saveResumeTime(src, audio.currentTime, audio.duration);
    }
    clearTimeout(resumeSaveTimer);
    window.removeEventListener('mousemove', onMove);
    window.removeEventListener('mouseup', onUp);
    window.removeEventListener('beforeunload', onBeforeUnload);
    window.removeEventListener('pagehide', onBeforeUnload);
    document.removeEventListener('click', onDocClick);
    document.removeEventListener('visibilitychange', onVisibilityChange);
    try {
      if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', null);
        navigator.mediaSession.setActionHandler('pause', null);
        navigator.mediaSession.setActionHandler('seekbackward', null);
        navigator.mediaSession.setActionHandler('seekforward', null);
        navigator.mediaSession.metadata = null;
      }
    } catch(e){}
  }

  return { el: card, cleanup };
}