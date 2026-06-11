"""No-build local browser suite for Rafiki's multimedia registry."""

from __future__ import annotations


def render_media_suite() -> bytes:
    return HTML.encode("utf-8")


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rafiki Suite</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #101114;
      --panel: #191b20;
      --panel-2: #22252b;
      --text: #f3f0e8;
      --muted: #aaa59a;
      --line: #343842;
      --accent: #4ecdc4;
      --warn: #ffcf5a;
      --bad: #ff6b6b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    header {
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      grid-template-columns: minmax(180px, 1fr) auto;
      gap: 16px;
      align-items: center;
      padding: 14px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(16, 17, 20, .96);
    }
    h1 { margin: 0; font-size: 18px; font-weight: 650; letter-spacing: 0; }
    h2 { margin: 0 0 12px; font-size: 15px; font-weight: 650; letter-spacing: 0; }
    nav { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; }
    button, select, input, textarea {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 6px;
      min-height: 34px;
      padding: 7px 10px;
      font: inherit;
    }
    button { cursor: pointer; }
    button.active, button.primary { border-color: var(--accent); color: var(--accent); }
    button.warn { border-color: var(--warn); color: var(--warn); }
    main { padding: 18px 20px 40px; }
    .toolbar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }
    .view { display: none; }
    .view.active { display: block; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 12px;
      align-items: start;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
      min-width: 0;
    }
    .subject-grid { grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
    .subject-profile .body {
      display: grid;
      gap: 12px;
    }
    .subject-header {
      display: flex;
      gap: 10px;
      justify-content: space-between;
      align-items: flex-start;
    }
    .subject-actions, .subject-project-links {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .subject-actions a, .subject-project-links a {
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--accent);
      min-height: 30px;
      padding: 6px 8px;
    }
    .subject-section {
      display: grid;
      gap: 6px;
      min-width: 0;
    }
    .subject-section h3 {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
      letter-spacing: 0;
    }
    .subject-list {
      display: grid;
      gap: 4px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .subject-list li { overflow-wrap: anywhere; }
    .subject-output-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
      gap: 8px;
    }
    .subject-output {
      display: grid;
      gap: 5px;
      min-width: 0;
    }
    .subject-output-thumb {
      aspect-ratio: 16 / 10;
      background: #0a0b0d;
      border: 1px solid var(--line);
      border-radius: 6px;
      display: grid;
      place-items: center;
      overflow: hidden;
    }
    .subject-output-thumb img, .subject-output-thumb video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .thumb {
      width: 100%;
      aspect-ratio: 16 / 10;
      background: #0a0b0d;
      display: grid;
      place-items: center;
      overflow: hidden;
    }
    .thumb img, .thumb video { width: 100%; height: 100%; object-fit: cover; }
    .thumb audio { width: 90%; }
    .body { padding: 10px; }
    .title { font-weight: 650; overflow-wrap: anywhere; }
    .meta { color: var(--muted); font-size: 12px; overflow-wrap: anywhere; margin-top: 4px; }
    .chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      color: var(--muted);
      font-size: 11px;
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 14px;
      margin-bottom: 14px;
    }
    .form {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .form .wide { grid-column: 1 / -1; }
    label { display: grid; gap: 5px; color: var(--muted); font-size: 12px; }
    label.check { display: flex; align-items: center; gap: 8px; }
    label.check input { min-height: 18px; width: 18px; }
    textarea { min-height: 120px; resize: vertical; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: var(--muted);
      background: #0d0e11;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      max-height: 300px;
      overflow: auto;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }
    th { color: var(--muted); font-size: 12px; font-weight: 600; }
    a { color: var(--accent); text-decoration: none; }
    #warnBadge { position: relative; }
    #warnBadge .badge {
      position: absolute;
      top: -5px;
      right: -5px;
      background: var(--warn);
      color: #101114;
      border-radius: 999px;
      font-size: 10px;
      font-weight: 700;
      line-height: 1;
      padding: 2px 5px;
      pointer-events: none;
    }
    #warnDrawer {
      display: none;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      padding: 12px 20px;
    }
    #warnDrawer.open { display: block; }
    #warnDrawer h3 { margin: 0 0 8px; font-size: 13px; color: var(--warn); }
    #warnDrawer ul { margin: 0; padding: 0 0 0 16px; color: var(--muted); font-size: 12px; }
    #warnDrawer li { margin-bottom: 4px; overflow-wrap: anywhere; }
    #warnDrawer .quiet { color: var(--muted); font-size: 12px; }
    @media (max-width: 760px) {
      header { grid-template-columns: 1fr; }
      nav { justify-content: flex-start; }
      .toolbar, .form { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Rafiki Suite</h1>
    <nav id="tabs">
      <button class="active" data-view="library">Library</button>
      <button data-view="subjects">Subjects</button>
      <button data-view="studio">Studio</button>
      <button data-view="jobs">Jobs</button>
      <button data-view="styles">Styles</button>
      <button data-view="video">Video Lab</button>
      <button id="refresh" title="Refresh media index">↻</button>
      <button id="warnBadge" title="Importer warnings" style="display:none">⚠</button>
    </nav>
  </header>
  <div id="warnDrawer">
    <h3>Importer Warnings</h3>
    <ul id="warnList"></ul>
  </div>
  <main>
    <section id="library" class="view active">
      <div class="toolbar">
        <select id="viewMode">
          <option value="review">Reviewable</option>
          <option value="all">All</option>
        </select>
        <input id="q" placeholder="Search">
        <select id="kind">
          <option value="">All kinds</option>
          <option>image</option><option>video</option><option>audio</option><option>prediction</option><option>style</option><option>prompt-suite</option><option>dataset</option><option>model-version</option>
        </select>
        <select id="collection">
          <option value="">All collections</option>
        </select>
        <select id="subject">
          <option value="">All subjects</option>
        </select>
        <button id="search" class="primary">Search</button>
      </div>
      <div id="summary" class="meta"></div>
      <div id="cards" class="grid"></div>
    </section>

    <section id="subjects" class="view">
      <div id="subjectCards" class="grid subject-grid"></div>
    </section>

    <section id="studio" class="view">
      <div class="panel">
        <h2>Image Studio</h2>
        <div class="form">
          <label class="wide">Prompt<textarea id="studioPrompt"></textarea></label>
          <label>Project<input id="studioProject" value="studio"></label>
          <label>Model<input id="studioModel" value="gemini-2.5-flash-image"></label>
          <label>Style<input id="studioStyle" value="kk"></label>
          <label>Aspect<input id="studioAspect" value="16:9"></label>
          <button id="studioRun" class="primary">Dry Run</button>
        </div>
      </div>
      <div class="panel">
        <h2>LoRA Training</h2>
        <div class="form">
          <label>Subject<input id="trainSubject" placeholder="kris"></label>
          <label>Dataset URL<input id="trainDataset"></label>
          <label class="check"><input type="checkbox" id="trainExecute"> Execute provider call</label>
          <label class="check"><input type="checkbox" id="trainConfirm"> Confirm execute spend</label>
          <button id="trainRun" class="warn">Dry Run</button>
        </div>
      </div>
      <div class="panel">
        <h2>Video Generation</h2>
        <div class="form">
          <label class="wide">Storyboard Path<input id="videoStoryboard" placeholder="/path/to/storyboard.json"></label>
          <label class="check"><input type="checkbox" id="videoExecute"> Execute provider call</label>
          <label class="check"><input type="checkbox" id="videoConfirm"> Confirm execute spend</label>
          <button id="videoRun" class="warn">Dry Run</button>
        </div>
      </div>
      <pre id="studioOut"></pre>
    </section>

    <section id="jobs" class="view">
      <table><thead><tr><th>Job</th><th>Status</th><th>Kind</th><th>Provider</th><th>Poll</th><th>Download</th><th>Last Checked</th><th>Target</th><th>Failure</th></tr></thead><tbody id="jobRows"></tbody></table>
    </section>

    <section id="styles" class="view">
      <div id="styleCards" class="grid"></div>
    </section>

    <section id="video" class="view">
      <div class="panel">
        <h2>Selection EDL</h2>
        <div class="form">
          <label>Include<select id="videoEdlInclude"><option value="focus,star">Focus + Star</option><option value="focus">Focus</option><option value="star">Star</option><option value="focus,star,exclude">All selection states</option></select></label>
          <label>Default Import<select id="videoImportDefault"><option value="focus">Focus</option><option value="star">Star</option><option value="exclude">Exclude</option></select></label>
          <button id="videoExport" class="primary">Export EDL</button>
          <button id="videoImport" class="warn">Import</button>
          <label class="wide">EDL JSON<textarea id="videoEdlJson"></textarea></label>
        </div>
      </div>
      <div class="toolbar">
        <input id="videoQ" placeholder="Filter clips">
        <select id="videoSubject"><option value="">All subjects</option></select>
        <select id="videoProject"><option value="">All projects</option></select>
        <button id="videoSearch" class="primary">Search</button>
        <a href="/library">Image Library</a>
      </div>
      <div id="videoCards" class="grid"></div>
    </section>
  </main>
  <script>
    const state = {
      entries: [],
      subjects: [],
      styles: [],
      jobs: [],
      selections: {},
      librarySubject: '',
      videoSubject: '',
      videoProject: '',
      initialView: ''
    };
    const $ = id => document.getElementById(id);

    function activateView(view) {
      const target = $(view) ? view : 'library';
      document.querySelectorAll('#tabs button[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === target));
      document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.id === target));
      pushFilterState();
    }

    document.querySelectorAll('#tabs button[data-view]').forEach(btn => {
      btn.addEventListener('click', () => activateView(btn.dataset.view));
    });

    $('refresh').addEventListener('click', () => loadAll(true));
    $('search').addEventListener('click', () => { pushFilterState(); loadMedia(false); });
    $('viewMode').addEventListener('change', () => { pushFilterState(); loadMedia(false); });
    $('kind').addEventListener('change', () => { pushFilterState(); loadMedia(false); });
    $('collection').addEventListener('change', () => { pushFilterState(); loadMedia(false); });
    $('subject').addEventListener('change', () => {
      state.librarySubject = $('subject').value;
      pushFilterState();
      loadMedia(false);
    });
    $('videoSubject').addEventListener('change', () => {
      state.videoSubject = $('videoSubject').value;
      pushFilterState();
      renderVideo();
    });
    $('videoProject').addEventListener('change', () => {
      state.videoProject = $('videoProject').value;
      pushFilterState();
      renderVideo();
    });
    $('videoSearch').addEventListener('click', renderVideo);
    $('videoExport').addEventListener('click', exportVideoEdl);
    $('videoImport').addEventListener('click', importVideoEdl);
    $('studioRun').addEventListener('click', runStudio);
    $('trainRun').addEventListener('click', runTraining);
    $('videoRun').addEventListener('click', runVideoGeneration);
    $('subjectCards').addEventListener('click', handleSubjectQuickLink);

    applyInitialParams();

    function mediaUrl(entry) {
      return '/media/' + encodeURIComponent(entry.root_key) + '/' + entry.relative_path.split('/').map(encodeURIComponent).join('/');
    }

    async function getJson(url) {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(await resp.text());
      return await resp.json();
    }

    async function postJson(url, payload) {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const text = await resp.text();
      if (!resp.ok) throw new Error(text);
      return JSON.parse(text || '{}');
    }

    const FILTER_STORAGE_KEY = 'rafiki:library-filters';

    function loadStoredFilters() {
      try {
        const raw = localStorage.getItem(FILTER_STORAGE_KEY);
        return raw ? JSON.parse(raw) : {};
      } catch (e) {
        return {};
      }
    }

    function pushFilterState() {
      const params = new URLSearchParams();
      const tab = document.querySelector('#tabs button.active[data-view]');
      const activeTab = tab ? tab.dataset.view : '';
      if (activeTab && activeTab !== 'library') params.set('tab', activeTab);
      const view = $('viewMode').value;
      if (view && view !== 'review') params.set('view', view);
      const q = $('q').value;
      if (q) params.set('q', q);
      const kind = $('kind').value;
      if (kind) params.set('kind', kind);
      const collection = $('collection').value;
      if (collection) params.set('collection', collection);
      const subject = $('subject').value;
      if (subject) params.set('subject', subject);
      const videoSubject = $('videoSubject').value;
      if (videoSubject) params.set('videoSubject', videoSubject);
      const videoProject = $('videoProject').value;
      if (videoProject) params.set('videoProject', videoProject);
      const search = params.toString();
      history.replaceState(null, '', search ? '?' + search : location.pathname);
      try {
        const stored = {tab: activeTab, view, q, kind, collection, subject, videoSubject, videoProject};
        localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(stored));
      } catch (e) { /* storage unavailable */ }
    }

    function applyInitialParams() {
      const urlParams = new URLSearchParams(window.location.search);
      const hasUrlState = urlParams.toString() !== '';
      const stored = hasUrlState ? {} : loadStoredFilters();
      const get = (key, fallback = '') => urlParams.has(key) ? (urlParams.get(key) || fallback) : (stored[key] || fallback);
      state.initialView = get('tab');
      state.librarySubject = get('subject');
      state.videoSubject = get('videoSubject');
      state.videoProject = get('videoProject');
      $('q').value = get('q');
      $('viewMode').value = get('view') || 'review';
      $('kind').value = get('kind');
      $('collection').value = get('collection');
    }

    async function loadMedia(refresh) {
      const params = new URLSearchParams();
      params.set('view', $('viewMode').value);
      if ($('q').value) params.set('q', $('q').value);
      if ($('kind').value) params.set('kind', $('kind').value);
      if ($('collection').value) params.set('collection', $('collection').value);
      const subject = state.librarySubject || $('subject').value;
      if (subject) params.set('subject', subject);
      if (refresh) params.set('refresh', '1');
      const data = await getJson('/api/media?' + params.toString());
      state.entries = data.entries || [];
      const total = data.total_entries || (data.summary && data.summary.entries) || state.entries.length;
      $('summary').textContent = `${state.entries.length} shown · ${total} indexed`;
      renderCollectionOptions(data.collections || []);
      renderCards();
      renderVideo();
    }

    function renderCollectionOptions(collections) {
      const current = $('collection').value;
      $('collection').innerHTML = '<option value="">All collections</option>' + collections.map(c => `<option>${escapeHtml(c)}</option>`).join('');
      $('collection').value = current;
    }

    function renderCards() {
      $('cards').innerHTML = state.entries.slice(0, 240).map(cardHtml).join('');
    }

    function cardHtml(entry) {
      const src = mediaUrl(entry);
      let media = `<span class="meta">${escapeHtml(entry.kind)}</span>`;
      if (entry.kind === 'image') media = `<img src="${src}" loading="lazy" alt="">`;
      if (entry.kind === 'video') media = `<video src="${src}" controls preload="metadata"></video>`;
      if (entry.kind === 'audio') media = `<audio src="${src}" controls></audio>`;
      const chips = [entry.kind, entry.collection, entry.subject, entry.project, entry.style].filter(Boolean);
      return `<article class="card">
        <div class="thumb">${media}</div>
        <div class="body">
          <div class="title">${escapeHtml(entry.title || entry.id)}</div>
          <div class="meta">${escapeHtml(entry.relative_path || entry.path)}</div>
          <div class="chips">${chips.map(chip => `<span class="chip">${escapeHtml(chip)}</span>`).join('')}</div>
        </div>
      </article>`;
    }

    async function loadSubjects() {
      const data = await getJson('/api/media/subjects');
      state.subjects = data.subjects || [];
      $('subjectCards').innerHTML = state.subjects.length
        ? state.subjects.map(subjectCardHtml).join('')
        : '<div class="meta">No subjects indexed</div>';
      renderSubjectFilterOptions();
      renderVideoSubjectOptions();
    }

    function subjectCardHtml(subject) {
      const quickLinks = subject.quick_links || {};
      const models = subject.model_versions || [];
      const outputs = subject.representative_outputs || [];
      const projectLinks = quickLinks.video_projects || [];
      return `<article class="card subject-profile"><div class="body">
        <div class="subject-header">
          <div>
            <div class="title">${escapeHtml(subject.display_name || subject.key)}</div>
            <div class="meta">${escapeHtml(subject.key || '')}${subject.trigger_word ? ' · ' + escapeHtml(subject.trigger_word) : ''}</div>
          </div>
          <div class="chips">
            <span class="chip">${Number(subject.entry_count || 0)} indexed</span>
            <span class="chip">${Number(subject.output_count || 0)} outputs</span>
            <span class="chip">${models.length} models</span>
          </div>
        </div>
        <div class="subject-actions">
          <a href="${escapeAttr(quickLinks.library || '#')}" data-library-subject="${escapeAttr(subject.key || '')}">Library</a>
          ${quickLinks.video_subject ? `<a href="${escapeAttr(quickLinks.video_subject)}" data-video-subject="${escapeAttr(subject.key || '')}">Video Lab</a>` : ''}
        </div>
        ${projectLinks.length ? `<div class="subject-project-links">${projectLinks.map(item => `<a href="${escapeAttr(item.href || '#')}" data-video-project="${escapeAttr(item.project || '')}">${escapeHtml(item.project || '')}</a>`).join('')}</div>` : ''}
        <div class="subject-section">
          <h3>Trigger Word</h3>
          <div class="meta">${escapeHtml(subject.trigger_word || 'Not indexed')}</div>
        </div>
        <div class="subject-section">
          <h3>Prompt Suites</h3>
          ${listHtml(subject.prompt_suites || [], 'No prompt suites indexed')}
        </div>
        <div class="subject-section">
          <h3>Album Roots</h3>
          ${listHtml(subject.album_roots || [], 'No album roots indexed')}
        </div>
        <div class="subject-section">
          <h3>Training Roots</h3>
          ${listHtml(subject.training_roots || [], 'No training roots indexed')}
        </div>
        <div class="subject-section">
          <h3>Model Versions</h3>
          ${modelVersionsHtml(models)}
        </div>
        <div class="subject-section">
          <h3>Top Outputs</h3>
          ${subjectOutputsHtml(outputs)}
        </div>
      </div></article>`;
    }

    function listHtml(items, emptyText) {
      if (!items.length) return `<div class="meta">${escapeHtml(emptyText)}</div>`;
      return `<ul class="subject-list">${items.map(item => `<li class="meta" title="${escapeAttr(item)}">${escapeHtml(shortPath(item))}</li>`).join('')}</ul>`;
    }

    function modelVersionsHtml(models) {
      if (!models.length) return '<div class="meta">No model versions indexed</div>';
      return `<ul class="subject-list">${models.map(model => {
        const title = [model.version, model.status].filter(Boolean).join(' · ') || 'Model version';
        const detail = model.model || model.source_manifest || '';
        return `<li><div>${escapeHtml(title)}</div><div class="meta">${escapeHtml(detail)}</div></li>`;
      }).join('')}</ul>`;
    }

    function subjectOutputsHtml(outputs) {
      if (!outputs.length) return '<div class="meta">No indexed outputs yet</div>';
      return `<div class="subject-output-grid">${outputs.map(output => `<div class="subject-output">
        <div class="subject-output-thumb">${entryMediaHtml(output)}</div>
        <div class="meta">${escapeHtml(output.title || output.id || output.kind)}</div>
      </div>`).join('')}</div>`;
    }

    function entryMediaHtml(entry) {
      if (entry.root_key && entry.relative_path && entry.kind === 'image') {
        return `<img src="${mediaUrl(entry)}" loading="lazy" alt="">`;
      }
      if (entry.root_key && entry.relative_path && entry.kind === 'video') {
        return `<video src="${mediaUrl(entry)}" controls preload="metadata"></video>`;
      }
      if (entry.root_key && entry.relative_path && entry.kind === 'audio') {
        return `<audio src="${mediaUrl(entry)}" controls></audio>`;
      }
      return `<span class="meta">${escapeHtml(entry.kind || 'media')}</span>`;
    }

    function shortPath(value) {
      const text = String(value || '');
      const parts = text.split('/').filter(Boolean);
      return parts.slice(-4).join('/') || text;
    }

    function renderSubjectFilterOptions() {
      const keys = subjectKeys();
      const current = state.librarySubject || $('subject').value;
      $('subject').innerHTML = '<option value="">All subjects</option>' + keys.map(key => `<option value="${escapeAttr(key)}">${escapeHtml(subjectLabel(key))}</option>`).join('');
      if (current) $('subject').value = current;
    }

    function renderVideoSubjectOptions() {
      const keys = subjectKeys();
      const current = state.videoSubject || $('videoSubject').value;
      $('videoSubject').innerHTML = '<option value="">All subjects</option>' + keys.map(key => `<option value="${escapeAttr(key)}">${escapeHtml(subjectLabel(key))}</option>`).join('');
      if (current) $('videoSubject').value = current;
    }

    function subjectKeys() {
      const fromSubjects = state.subjects.map(subject => subject.key).filter(Boolean);
      const fromEntries = state.entries.map(entry => entry.subject).filter(Boolean);
      return [...new Set([...fromSubjects, ...fromEntries])].sort();
    }

    function subjectLabel(key) {
      const subject = state.subjects.find(item => item.key === key);
      return subject ? (subject.display_name || key) : key;
    }

    async function loadStyles() {
      const data = await getJson('/api/media/styles');
      state.styles = data.styles || [];
      $('styleCards').innerHTML = state.styles.map(s => `<article class="card"><div class="body">
        <div class="title">${escapeHtml(s.name)}</div>
        <div class="meta">${escapeHtml(s.source)}</div>
        <pre>${escapeHtml((s.suffix || '').slice(0, 900))}</pre>
      </div></article>`).join('');
    }

    async function loadJobs() {
      const data = await getJson('/api/media/jobs');
      state.jobs = data.jobs || [];
      $('jobRows').innerHTML = state.jobs.map(j => `<tr>
        <td>${escapeHtml(j.id)}</td>
        <td>${escapeHtml(j.status)}</td>
        <td>${escapeHtml(j.kind)}</td>
        <td>${providerCell(j)}</td>
        <td>${escapeHtml(j.polling_status || '')}</td>
        <td>${escapeHtml(j.output_download_state || '')}</td>
        <td>${escapeHtml(j.last_checked_at || '')}</td>
        <td>${escapeHtml(j.target_output_dir || '')}<div class="meta">${escapeHtml(jobCostText(j))}</div></td>
        <td>${escapeHtml(jobFailureText(j))}</td>
      </tr>`).join('');
    }

    function providerCell(job) {
      const label = job.provider || 'provider';
      if (!job.provider_url) return escapeHtml(label);
      return `<a href="${escapeHtml(job.provider_url)}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`;
    }

    function jobCostText(job) {
      const estimate = job.cost_estimate || {};
      const counts = estimate.counts || {};
      const parts = [];
      if (estimate.basis) parts.push(estimate.basis);
      if (counts.planned_provider_jobs !== undefined) parts.push(`${counts.planned_provider_jobs} planned job`);
      if (counts.storyboard_scenes !== undefined) parts.push(`${counts.storyboard_scenes} scene`);
      if (counts.steps !== undefined) parts.push(`${counts.steps} steps`);
      return parts.join(' · ');
    }

    function jobFailureText(job) {
      if (job.error) return job.error;
      const details = job.failure_details || {};
      return Object.keys(details).map(key => `${key}: ${details[key]}`).join(' · ');
    }

    async function loadSelections() {
      const data = await getJson('/api/media/selections');
      state.selections = data.items || {};
    }

    async function loadWarnings() {
      const data = await getJson('/api/media/warnings');
      const warnings = data.warnings || [];
      const badge = $('warnBadge');
      const drawer = $('warnDrawer');
      const list = $('warnList');
      if (warnings.length) {
        badge.style.display = '';
        badge.innerHTML = `⚠ <span class="badge">${warnings.length}</span>`;
        list.innerHTML = warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('');
      } else {
        badge.style.display = 'none';
        drawer.classList.remove('open');
        list.innerHTML = '';
      }
    }

    $('warnBadge').addEventListener('click', () => {
      $('warnDrawer').classList.toggle('open');
    });

    function renderVideo() {
      const q = $('videoQ').value.toLowerCase();
      const subject = state.videoSubject || $('videoSubject').value;
      const project = state.videoProject || $('videoProject').value;
      const videos = state.entries.filter(e => e.kind === 'video')
        .filter(e => !subject || e.subject === subject)
        .filter(e => !project || e.project === project)
        .filter(e => !q || [e.title, e.subject, e.project, e.relative_path, e.prompt].join(' ').toLowerCase().includes(q));
      const projects = [...new Set(state.entries.filter(e => e.kind === 'video').map(e => e.project).filter(Boolean))].sort();
      const current = $('videoProject').value;
      $('videoProject').innerHTML = '<option value="">All projects</option>' + projects.map(p => `<option>${escapeHtml(p)}</option>`).join('');
      $('videoProject').value = state.videoProject || current;
      renderVideoSubjectOptions();
      $('videoCards').innerHTML = videos.slice(0, 160).map(videoCardHtml).join('');
      document.querySelectorAll('[data-select]').forEach(btn => btn.addEventListener('click', saveSelection));
    }

    function videoCardHtml(entry) {
      const current = state.selections[entry.id] || '';
      return `<article class="card">
        <div class="thumb"><video src="${mediaUrl(entry)}" controls preload="metadata"></video></div>
        <div class="body">
          <div class="title">${escapeHtml(entry.title || entry.id)}</div>
          <div class="meta">${escapeHtml(entry.project || '')} ${escapeHtml(entry.relative_path)}</div>
          <div class="chips">
            ${['focus','star','exclude'].map(value => `<button data-select="${value}" data-id="${entry.id}" class="${current === value ? 'active' : ''}">${value}</button>`).join('')}
          </div>
        </div>
      </article>`;
    }

    async function saveSelection(event) {
      const btn = event.currentTarget;
      await postJson('/api/media/selections', {key: btn.dataset.id, value: btn.dataset.select});
      state.selections[btn.dataset.id] = btn.dataset.select;
      renderVideo();
    }

    async function exportVideoEdl() {
      const params = new URLSearchParams();
      params.set('include', $('videoEdlInclude').value);
      const result = await getJson('/api/media/selections/edl?' + params.toString());
      $('videoEdlJson').value = JSON.stringify(result, null, 2);
    }

    async function importVideoEdl() {
      const raw = $('videoEdlJson').value.trim();
      if (!raw) return;
      const result = await postJson('/api/media/selections/import', {
        edl: JSON.parse(raw),
        default_selection: $('videoImportDefault').value,
        replace: true
      });
      state.selections = result.items || {};
      renderVideo();
    }

    function handleSubjectQuickLink(event) {
      const libraryLink = event.target.closest('[data-library-subject]');
      if (libraryLink) {
        event.preventDefault();
        applyLibrarySubject(libraryLink.dataset.librarySubject || '', libraryLink.getAttribute('href') || '');
        return;
      }
      const videoSubjectLink = event.target.closest('[data-video-subject]');
      if (videoSubjectLink) {
        event.preventDefault();
        applyVideoSubject(videoSubjectLink.dataset.videoSubject || '', videoSubjectLink.getAttribute('href') || '');
        return;
      }
      const videoProjectLink = event.target.closest('[data-video-project]');
      if (videoProjectLink) {
        event.preventDefault();
        applyVideoProject(videoProjectLink.dataset.videoProject || '', videoProjectLink.getAttribute('href') || '');
      }
    }

    async function applyLibrarySubject(subject, _href) {
      state.librarySubject = subject;
      $('subject').value = subject;
      $('viewMode').value = 'all';
      activateView('library');
      await loadMedia(false);
    }

    function applyVideoSubject(subject, _href) {
      state.videoSubject = subject;
      $('videoSubject').value = subject;
      activateView('video');
      renderVideo();
    }

    async function applyVideoProject(project, _href) {
      state.videoSubject = '';
      state.videoProject = project;
      $('videoSubject').value = '';
      $('videoProject').value = project;
      activateView('video');
      if (state.librarySubject) {
        state.librarySubject = '';
        $('subject').value = '';
        await loadMedia(false);
      } else {
        renderVideo();
      }
    }

    async function runStudio() {
      const result = await postJson('/api/regen', {
        mode: 'single',
        dry_run: true,
        prompt: $('studioPrompt').value,
        project: $('studioProject').value,
        model: $('studioModel').value,
        style: $('studioStyle').value,
        aspect_ratio: $('studioAspect').value
      });
      $('studioOut').textContent = JSON.stringify(result, null, 2);
    }

    async function runTraining() {
      const execute = $('trainExecute').checked;
      const confirmExecute = $('trainConfirm').checked;
      if (execute && (!confirmExecute || !window.confirm('Execute LoRA training through Replicate?'))) {
        $('studioOut').textContent = 'Training execute mode needs explicit confirmation.';
        return;
      }
      const result = await postJson('/api/jobs/train-lora', {
        subject: $('trainSubject').value,
        input_images_url: $('trainDataset').value,
        execute,
        confirm_execute: confirmExecute
      });
      $('studioOut').textContent = JSON.stringify(result, null, 2);
      loadJobs();
    }

    async function runVideoGeneration() {
      const execute = $('videoExecute').checked;
      const confirmExecute = $('videoConfirm').checked;
      if (execute && (!confirmExecute || !window.confirm('Execute video generation through Replicate?'))) {
        $('studioOut').textContent = 'Video execute mode needs explicit confirmation.';
        return;
      }
      const result = await postJson('/api/jobs/video-generate', {
        storyboard: $('videoStoryboard').value,
        execute,
        confirm_execute: confirmExecute
      });
      $('studioOut').textContent = JSON.stringify(result, null, 2);
      loadJobs();
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    }

    function escapeAttr(value) {
      return escapeHtml(value);
    }

    async function loadAll(refresh=false) {
      await loadMedia(refresh);
      await Promise.all([loadSubjects(), loadStyles(), loadJobs(), loadSelections(), loadWarnings()]);
      renderVideo();
      if (state.initialView) activateView(state.initialView);
      pushFilterState();
    }
    loadAll(false).catch(err => { $('summary').textContent = err.message; });
  </script>
</body>
</html>
"""
