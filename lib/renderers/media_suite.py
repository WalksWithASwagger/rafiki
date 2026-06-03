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
      grid-template-columns: minmax(220px, 1fr) 140px 140px auto;
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
    </nav>
  </header>
  <main>
    <section id="library" class="view active">
      <div class="toolbar">
        <input id="q" placeholder="Search">
        <select id="kind">
          <option value="">All kinds</option>
          <option>image</option><option>video</option><option>audio</option><option>dataset</option><option>prediction</option><option>style</option>
        </select>
        <select id="collection">
          <option value="">All collections</option>
        </select>
        <button id="search" class="primary">Search</button>
      </div>
      <div id="summary" class="meta"></div>
      <div id="cards" class="grid"></div>
    </section>

    <section id="subjects" class="view">
      <div id="subjectCards" class="grid"></div>
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
          <button id="trainRun" class="warn">Dry Run</button>
        </div>
      </div>
      <div class="panel">
        <h2>Video Generation</h2>
        <div class="form">
          <label class="wide">Storyboard Path<input id="videoStoryboard" placeholder="/path/to/storyboard.json"></label>
          <button id="videoRun" class="warn">Dry Run</button>
        </div>
      </div>
      <pre id="studioOut"></pre>
    </section>

    <section id="jobs" class="view">
      <table><thead><tr><th>Job</th><th>Status</th><th>Kind</th><th>Target</th></tr></thead><tbody id="jobRows"></tbody></table>
    </section>

    <section id="styles" class="view">
      <div id="styleCards" class="grid"></div>
    </section>

    <section id="video" class="view">
      <div class="toolbar">
        <input id="videoQ" placeholder="Filter clips">
        <select id="videoProject"><option value="">All projects</option></select>
        <button id="videoSearch" class="primary">Search</button>
        <a href="/library">Image Library</a>
      </div>
      <div id="videoCards" class="grid"></div>
    </section>
  </main>
  <script>
    const state = { entries: [], subjects: [], styles: [], jobs: [], selections: {} };
    const $ = id => document.getElementById(id);

    document.querySelectorAll('#tabs button[data-view]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#tabs button[data-view]').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        btn.classList.add('active');
        $(btn.dataset.view).classList.add('active');
      });
    });

    $('refresh').addEventListener('click', () => loadAll(true));
    $('search').addEventListener('click', () => loadMedia(false));
    $('videoSearch').addEventListener('click', renderVideo);
    $('studioRun').addEventListener('click', runStudio);
    $('trainRun').addEventListener('click', runTraining);
    $('videoRun').addEventListener('click', runVideoGeneration);

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

    async function loadMedia(refresh) {
      const params = new URLSearchParams();
      if ($('q').value) params.set('q', $('q').value);
      if ($('kind').value) params.set('kind', $('kind').value);
      if ($('collection').value) params.set('collection', $('collection').value);
      if (refresh) params.set('refresh', '1');
      const data = await getJson('/api/media?' + params.toString());
      state.entries = data.entries || [];
      $('summary').textContent = `${state.entries.length} entries`;
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
      $('subjectCards').innerHTML = state.subjects.map(s => `<article class="card"><div class="body">
        <div class="title">${escapeHtml(s.display_name)}</div>
        <div class="meta">${escapeHtml(s.key)} · ${escapeHtml(s.trigger_word || '')}</div>
        <div class="chips"><span class="chip">${s.prompt_suites.length} suites</span><span class="chip">${s.model_versions.length} models</span></div>
      </div></article>`).join('');
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
        <td>${escapeHtml(j.id)}</td><td>${escapeHtml(j.status)}</td><td>${escapeHtml(j.kind)}</td><td>${escapeHtml(j.target_output_dir || '')}</td>
      </tr>`).join('');
    }

    async function loadSelections() {
      const data = await getJson('/api/media/selections');
      state.selections = data.items || {};
    }

    function renderVideo() {
      const q = $('videoQ').value.toLowerCase();
      const project = $('videoProject').value;
      const videos = state.entries.filter(e => e.kind === 'video')
        .filter(e => !project || e.project === project)
        .filter(e => !q || [e.title, e.project, e.relative_path, e.prompt].join(' ').toLowerCase().includes(q));
      const projects = [...new Set(state.entries.filter(e => e.kind === 'video').map(e => e.project).filter(Boolean))].sort();
      const current = $('videoProject').value;
      $('videoProject').innerHTML = '<option value="">All projects</option>' + projects.map(p => `<option>${escapeHtml(p)}</option>`).join('');
      $('videoProject').value = current;
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
      const result = await postJson('/api/jobs/train-lora', {
        subject: $('trainSubject').value,
        input_images_url: $('trainDataset').value
      });
      $('studioOut').textContent = JSON.stringify(result, null, 2);
      loadJobs();
    }

    async function runVideoGeneration() {
      const result = await postJson('/api/jobs/video-generate', {
        storyboard: $('videoStoryboard').value
      });
      $('studioOut').textContent = JSON.stringify(result, null, 2);
      loadJobs();
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    }

    async function loadAll(refresh=false) {
      await loadMedia(refresh);
      await Promise.all([loadSubjects(), loadStyles(), loadJobs(), loadSelections()]);
      renderVideo();
    }
    loadAll(false).catch(err => { $('summary').textContent = err.message; });
  </script>
</body>
</html>
"""
