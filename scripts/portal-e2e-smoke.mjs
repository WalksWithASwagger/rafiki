#!/usr/bin/env node

import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';
import puppeteer from 'puppeteer';
import sharp from 'sharp';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');

function commandWorks(command) {
  const result = spawnSync(command, ['--version'], { encoding: 'utf8' });
  return result.status === 0;
}

function getPythonExecutable() {
  const winVenv = path.join(repoRoot, '.venv', 'Scripts', 'python.exe');
  const unixVenv = path.join(repoRoot, '.venv', 'bin', 'python');
  const unixVenvPython3 = path.join(repoRoot, '.venv', 'bin', 'python3');

  if (process.platform === 'win32' && fs.existsSync(winVenv)) return winVenv;
  if (fs.existsSync(unixVenv)) return unixVenv;
  if (fs.existsSync(unixVenvPython3)) return unixVenvPython3;
  if (commandWorks('python3')) return 'python3';
  return 'python';
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: repoRoot,
    encoding: 'utf8',
    ...options,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(
      [
        `${command} ${args.join(' ')} failed with ${result.status}`,
        result.stdout,
        result.stderr,
      ].filter(Boolean).join('\n'),
    );
  }
  return result;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function envIsSet(name) {
  return Boolean(process.env[name]);
}

function resolveVisualArtifactDir(tmpRoot, keepTmp) {
  const configured = process.env.RAFIKI_E2E_ARTIFACT_DIR?.trim();
  if (configured) return path.resolve(repoRoot, configured);
  if (keepTmp) return path.join(tmpRoot, 'visual-artifacts');
  return null;
}

function saveVisualArtifact(artifactDir, source, fileName) {
  if (!artifactDir) return null;
  fs.mkdirSync(artifactDir, { recursive: true });
  const target = path.join(artifactDir, fileName);
  fs.copyFileSync(source, target);
  return target;
}

function requestStatus(url) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, (res) => {
      res.resume();
      res.on('end', () => resolve(res.statusCode || 0));
    });
    req.on('error', reject);
    req.setTimeout(1000, () => {
      req.destroy(new Error('request timeout'));
    });
  });
}

async function waitForServer(url, server) {
  const startedAt = Date.now();
  let lastError = null;
  while (Date.now() - startedAt < 15000) {
    if (server.exitCode !== null) {
      throw new Error(`portal server exited early with ${server.exitCode}`);
    }
    try {
      const status = await requestStatus(url);
      if (status === 200) return;
      lastError = new Error(`status ${status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`portal server did not become ready: ${lastError?.message || 'unknown'}`);
}

async function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = http.createServer();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = typeof address === 'object' && address ? address.port : null;
      server.close(() => {
        if (port) resolve(port);
        else reject(new Error('could not allocate port'));
      });
    });
  });
}

async function writeFixtureImage(target, index, aspectRatio) {
  const [w, h] = aspectRatio === '16:9' ? [960, 540] : [720, 720];
  const hue = index === 0 ? '#18b7a5' : '#8b6cff';
  const svg = `
    <svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#111827"/>
          <stop offset="100%" stop-color="${hue}"/>
        </linearGradient>
      </defs>
      <rect width="${w}" height="${h}" fill="url(#bg)"/>
      <circle cx="${Math.round(w * 0.28)}" cy="${Math.round(h * 0.42)}" r="${Math.round(Math.min(w, h) * 0.16)}" fill="#f7f4e9" opacity="0.88"/>
      <path d="M ${Math.round(w * 0.18)} ${Math.round(h * 0.74)} C ${Math.round(w * 0.36)} ${Math.round(h * 0.52)}, ${Math.round(w * 0.56)} ${Math.round(h * 0.84)}, ${Math.round(w * 0.82)} ${Math.round(h * 0.28)}" fill="none" stroke="#f4d35e" stroke-width="12" stroke-linecap="round" opacity="0.82"/>
      <text x="${Math.round(w * 0.08)}" y="${Math.round(h * 0.16)}" fill="#ffffff" font-family="Arial, sans-serif" font-size="${Math.round(Math.min(w, h) * 0.07)}" font-weight="700">Rafiki E2E ${index + 1}</text>
    </svg>`;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  await sharp(Buffer.from(svg)).png().toFile(target);
}

async function screenshotStats(filePath) {
  const metadata = await sharp(filePath).metadata();
  const stats = await sharp(filePath).stats();
  const stdev = stats.channels.map((channel) => Number(channel.stdev.toFixed(2)));
  const { data, info } = await sharp(filePath)
    .removeAlpha()
    .resize({ width: 320, withoutEnlargement: true })
    .raw()
    .toBuffer({ resolveWithObject: true });
  const pixels = data.length / info.channels;
  let lumaTotal = 0;
  let darkPixels = 0;
  let brightPixels = 0;
  let saturatedPixels = 0;
  const colorBuckets = new Set();

  for (let index = 0; index < data.length; index += info.channels) {
    const r = data[index];
    const g = data[index + 1];
    const b = data[index + 2];
    const luma = (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    lumaTotal += luma;
    if (luma < 35) darkPixels += 1;
    if (luma > 225) brightPixels += 1;
    if (max - min > 24) saturatedPixels += 1;
    colorBuckets.add(`${r >> 5}:${g >> 5}:${b >> 5}`);
  }

  return {
    file: filePath,
    width: metadata.width || 0,
    height: metadata.height || 0,
    stdev,
    nonblank: stdev.some((value) => value > 2),
    visual: {
      meanLuma: Number((lumaTotal / pixels).toFixed(2)),
      darkRatio: Number((darkPixels / pixels).toFixed(3)),
      brightRatio: Number((brightPixels / pixels).toFixed(3)),
      saturatedRatio: Number((saturatedPixels / pixels).toFixed(3)),
      colorBuckets: colorBuckets.size,
    },
  };
}

function assertVisualBaseline(label, stats, rules) {
  assert(stats.nonblank, `${label} screenshot is blank`);
  assert(stats.width >= rules.minWidth, `${label} screenshot is too narrow: ${stats.width}`);
  assert(stats.height >= rules.minHeight, `${label} screenshot is too short: ${stats.height}`);
  assert(stats.visual.colorBuckets >= rules.minColorBuckets, `${label} screenshot has too few color buckets: ${stats.visual.colorBuckets}`);
  assert(stats.visual.saturatedRatio >= rules.minSaturatedRatio, `${label} screenshot lost too much color: ${stats.visual.saturatedRatio}`);
  assert(stats.visual.darkRatio >= rules.minDarkRatio, `${label} screenshot lost dark UI/content contrast: ${stats.visual.darkRatio}`);
  assert(stats.visual.brightRatio <= rules.maxBrightRatio, `${label} screenshot is washed out: ${stats.visual.brightRatio}`);
  assert(
    stats.visual.meanLuma >= rules.minMeanLuma && stats.visual.meanLuma <= rules.maxMeanLuma,
    `${label} screenshot luminance drifted outside baseline: ${stats.visual.meanLuma}`,
  );
}

async function main() {
  const python = getPythonExecutable();
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'rafiki-portal-e2e-'));
  const keepTmp = envIsSet('RAFIKI_E2E_KEEP_TMP');
  const visualArtifactDir = resolveVisualArtifactDir(tmpRoot, keepTmp);
  const outputRoot = path.join(tmpRoot, 'output');
  const project = 'e2e-showpiece-smoke';
  const projectDir = path.join(outputRoot, project);
  const errors = [];
  let server = null;
  let browser = null;

  try {
    fs.mkdirSync(outputRoot, { recursive: true });
    run(python, [
      'generate.py',
      '--prompt-file',
      'examples/quickstart-image-prompts.md',
      '--output-dir',
      projectDir,
      '--model',
      'gemini',
      '--style',
      'none',
      '--aspect-ratio',
      'square',
      '--dry-run',
      '--json',
    ]);

    const runDir = fs.readdirSync(projectDir)
      .filter((name) => name.startsWith('run-'))
      .map((name) => path.join(projectDir, name))
      .find((candidate) => fs.statSync(candidate).isDirectory());
    assert(runDir, 'dry run did not create a run directory');

    const manifestPath = path.join(runDir, 'run.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    assert(Array.isArray(manifest.images) && manifest.images.length === 2, 'expected two fixture images in run manifest');

    await Promise.all(manifest.images.map((image, index) => {
      const target = path.join(runDir, image.file);
      return writeFixtureImage(target, index, image.aspect_ratio || manifest.aspect_ratio || '1:1');
    }));

    run(python, ['generate.py', 'library', '--output-dir', outputRoot]);

    const port = await getFreePort();
    const url = `http://127.0.0.1:${port}/`;
    server = spawn(python, ['generate.py', 'serve', '--port', String(port), '--output-dir', outputRoot], {
      cwd: repoRoot,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        GOOGLE_API_KEY: '',
        GEMINI_API_KEY: '',
        OPENAI_API_KEY: '',
      },
    });

    let serverOutput = '';
    server.stdout.on('data', (chunk) => { serverOutput += chunk.toString(); });
    server.stderr.on('data', (chunk) => { serverOutput += chunk.toString(); });

    await waitForServer(url, server);

    const usage = await fetch(`${url}api/usage`).then((response) => response.json());
    assert(usage.archive.projects === 1, `expected one project, got ${usage.archive.projects}`);
    assert(usage.archive.runs === 1, `expected one run, got ${usage.archive.runs}`);
    assert(usage.archive.images === 2, `expected two images, got ${usage.archive.images}`);

    const readiness = await fetch(`${url}api/deploy-readiness`).then((response) => response.json());
    assert(Array.isArray(readiness.checks), 'deploy readiness did not return checks');
    assert(!JSON.stringify(readiness).toLowerCase().includes('secret'), 'deploy readiness leaked a secret-like value');

    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const desktop = await browser.newPage();
    desktop.on('pageerror', (error) => errors.push(`desktop pageerror: ${error.message}`));
    desktop.on('console', (msg) => {
      if (['error', 'warning'].includes(msg.type())) errors.push(`desktop console ${msg.type()}: ${msg.text()}`);
    });
    await desktop.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });
    await desktop.goto(url, { waitUntil: 'networkidle0' });
    await desktop.waitForSelector('.card', { timeout: 5000 });

    const desktopState = await desktop.evaluate(async () => {
      const countVisible = () => document.querySelectorAll('.card:not(.hidden-filter)').length;
      const first = document.querySelector('.card');
      const titleInput = document.querySelector('#metadata-title');
      const tagsInput = document.querySelector('#metadata-tags');
      const feedbackStatus = document.querySelector('#feedback-status');
      const feedbackNote = document.querySelector('#feedback-note');
      const evaluationDecision = document.querySelector('#evaluation-decision');
      const evaluationScore = document.querySelector('#evaluation-score');
      const evaluationUseCase = document.querySelector('#evaluation-use-case');
      const evaluationRationale = document.querySelector('#evaluation-rationale');
      const evaluationNextStep = document.querySelector('#evaluation-next-step');
      const cssText = Array.from(document.querySelectorAll('style'))
        .map((style) => style.textContent || '')
        .join('\n');

      const initialMode = document.querySelector('.portal-mode-btn.active')?.dataset.modeTarget || '';
      const reviewVisible = !document.querySelector('#portal-mode-review').hidden;
      setPortalMode('teach');
      const teachVisible = !document.querySelector('#portal-mode-teach').hidden;
      const teachButton = document.querySelector('.portal-mode-btn[data-mode-target="teach"]');
      teachButton.focus();
      const teachFocusStyle = window.getComputedStyle(teachButton);
      const atlasPrograms = document.querySelectorAll('.atlas-program').length;
      const atlasModules = document.querySelectorAll('.atlas-module').length;
      const atlasFacilitatorNotes = document.querySelectorAll('.atlas-facilitator-notes li').length;
      const atlasRubricItems = document.querySelectorAll('.atlas-rubric-item').length;
      const atlasConceptLinks = document.querySelectorAll('.atlas-concept-link').length;
      const atlasGraphNodes = document.querySelectorAll('.atlas-graph-nodes g').length;
      const atlasGraphEdges = document.querySelectorAll('.atlas-graph-edges line').length;
      focusAtlasUnmapped();
      const atlasFilterVisible = countVisible();
      const atlasBannerVisible = !document.querySelector('#atlas-filter-banner').hidden;
      clearAtlasAssetFilter();
      setPortalMode('generate');
      const generateVisible = !document.querySelector('#portal-mode-generate').hidden;
      setPortalMode('curate');
      const curateVisible = !document.querySelector('#portal-mode-curate').hidden;
      setPortalMode('spend');
      const spendVisible = !document.querySelector('#portal-mode-spend').hidden;
      setPortalMode('review');

      document.querySelector('#search').value = 'review portal';
      document.querySelector('#search').dispatchEvent(new Event('input', { bubbles: true }));
      const searchVisible = countVisible();
      document.querySelector('#search').value = '';
      document.querySelector('#search').dispatchEvent(new Event('input', { bubbles: true }));

      openRunDetail({ preventDefault() {}, stopPropagation() {} }, 0);

      titleInput.value = 'E2E World-Class Smoke Card';
      tagsInput.value = 'e2e,showpiece';
      await saveMetadataForDetail({ preventDefault() {}, stopPropagation() {} });

      feedbackStatus.value = 'keep';
      feedbackNote.value = 'Browser E2E note';
      await saveFeedbackForDetail({ preventDefault() {}, stopPropagation() {} });

      evaluationDecision.value = 'approve';
      evaluationScore.value = '5';
      evaluationUseCase.value = 'homepage hero';
      evaluationRationale.value = 'Browser E2E evaluation note';
      evaluationNextStep.value = 'Export with the smoke bundle';
      await saveEvaluationForDetail({ preventDefault() {}, stopPropagation() {} });

      setRating(first.dataset.ratingKey, null);
      applyRating(first, first.dataset.ratingKey);
      setRating(first.dataset.ratingKey, 'star');
      applyRating(first, first.dataset.ratingKey);
      setRatingFilter('star');
      const starFilterVisible = countVisible();
      setRatingFilter('review-queue');
      const reviewQueueVisible = countVisible();
      setRatingFilter('all');

      return {
        title: document.title,
        initialMode,
        reviewVisible,
        modeChecks: {
          teachVisible,
          generateVisible,
          curateVisible,
          spendVisible,
        },
        atlas: {
          programs: atlasPrograms,
          modules: atlasModules,
          facilitatorNotes: atlasFacilitatorNotes,
          rubricItems: atlasRubricItems,
          conceptLinks: atlasConceptLinks,
          graphNodes: atlasGraphNodes,
          graphEdges: atlasGraphEdges,
          filterVisible: atlasFilterVisible,
          bannerVisible: atlasBannerVisible,
        },
        quality: {
          focusedTeachModeButton: document.activeElement === teachButton,
          teachFocusOutline: teachFocusStyle.outlineStyle,
          teachFocusShadow: teachFocusStyle.boxShadow,
          hasFocusVisibleCss: cssText.includes(':focus-visible'),
          hasReducedMotionCss: cssText.includes('prefers-reduced-motion'),
          hasTransitionAll: /transition\s*:\s*all\b/i.test(cssText),
          lineageChips: document.querySelectorAll('.lineage-chip').length,
          copyPromptButtons: document.querySelectorAll('.lineage-copy').length,
          reviewQueueCount: document.querySelector('#fc-review-queue')?.textContent?.trim() || '',
          evaluationBadges: document.querySelectorAll('.evaluation-badge.evaluation-on').length,
        },
        cards: document.querySelectorAll('.card').length,
        visibleCards: countVisible(),
        imageNaturalWidths: Array.from(document.querySelectorAll('.card img')).map((img) => img.naturalWidth),
        searchVisible,
        detailOpen: document.querySelector('#run-detail-panel').getAttribute('aria-hidden') === 'false',
        metadataStatus: document.querySelector('#metadata-status-message').textContent.trim(),
        feedbackStatus: document.querySelector('#feedback-status-message').textContent.trim(),
        evaluationStatus: document.querySelector('#evaluation-status-message').textContent.trim(),
        runDecisionSummary: document.querySelector('#run-decision-summary')?.textContent || '',
        starFilterVisible,
        reviewQueueVisible,
        overflow: {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          bodyScrollWidth: document.body.scrollWidth,
        },
        ops: {
          images: document.querySelector('#usage-image-count')?.textContent?.trim(),
          runs: document.querySelector('#usage-run-count')?.textContent?.trim(),
        },
      };
    });

    assert(desktopState.title === 'Rafiki Library', `unexpected title: ${desktopState.title}`);
    assert(desktopState.initialMode === 'review', `expected review mode by default, got ${desktopState.initialMode}`);
    assert(desktopState.reviewVisible, 'review mode was hidden by default');
    assert(desktopState.modeChecks.teachVisible, 'teach mode did not become visible');
    assert(desktopState.modeChecks.generateVisible, 'generate mode did not become visible');
    assert(desktopState.modeChecks.curateVisible, 'curate mode did not become visible');
    assert(desktopState.modeChecks.spendVisible, 'spend mode did not become visible');
    assert(desktopState.atlas.programs >= 1, 'curriculum atlas did not render programs');
    assert(desktopState.atlas.modules >= 1, 'curriculum atlas did not render modules');
    assert(desktopState.atlas.facilitatorNotes >= 1, 'curriculum atlas did not render facilitator notes');
    assert(desktopState.atlas.rubricItems >= 1, 'curriculum atlas did not render critique rubric items');
    assert(desktopState.atlas.conceptLinks >= 1, 'curriculum atlas did not render concept links');
    assert(desktopState.atlas.graphNodes >= 1, 'curriculum atlas concept graph did not render nodes');
    assert(desktopState.atlas.graphEdges >= 1, 'curriculum atlas concept graph did not render edges');
    assert(desktopState.atlas.filterVisible === 2, `unmapped atlas filter should show two cards, got ${desktopState.atlas.filterVisible}`);
    assert(desktopState.atlas.bannerVisible, 'atlas filter banner did not appear');
    assert(desktopState.quality.focusedTeachModeButton, 'teach mode button did not accept focus');
    assert(desktopState.quality.hasFocusVisibleCss, 'portal CSS is missing focus-visible guardrails');
    assert(desktopState.quality.hasReducedMotionCss, 'portal CSS is missing prefers-reduced-motion guardrails');
    assert(!desktopState.quality.hasTransitionAll, 'portal CSS still contains transition: all');
    assert(desktopState.quality.lineageChips >= 6, 'card lineage chips did not render');
    assert(desktopState.quality.copyPromptButtons === 2, `expected two copy prompt buttons, got ${desktopState.quality.copyPromptButtons}`);
    assert(desktopState.cards === 2, `expected two cards, got ${desktopState.cards}`);
    assert(desktopState.visibleCards === 2, `expected two visible cards, got ${desktopState.visibleCards}`);
    assert(desktopState.imageNaturalWidths.every((width) => width > 0), 'desktop images did not load');
    assert(desktopState.searchVisible === 1, `search should show one card, got ${desktopState.searchVisible}`);
    assert(desktopState.detailOpen, 'detail panel did not open');
    assert(desktopState.metadataStatus === 'Saved', `metadata save failed: ${desktopState.metadataStatus}`);
    assert(desktopState.feedbackStatus === 'Saved', `feedback save failed: ${desktopState.feedbackStatus}`);
    assert(desktopState.evaluationStatus === 'Saved', `evaluation save failed: ${desktopState.evaluationStatus}`);
    assert(desktopState.quality.evaluationBadges >= 1, 'evaluation badge did not render after save');
    assert(desktopState.runDecisionSummary.includes('Approve 1'), `run decision summary did not count approval: ${desktopState.runDecisionSummary}`);
    assert(desktopState.runDecisionSummary.includes('Avg score 5.0'), `run decision summary did not average score: ${desktopState.runDecisionSummary}`);
    assert(desktopState.starFilterVisible === 1, `star filter should show one card, got ${desktopState.starFilterVisible}`);
    assert(desktopState.reviewQueueVisible === 2, `review queue should show two cards, got ${desktopState.reviewQueueVisible}`);
    assert(desktopState.overflow.scrollWidth <= desktopState.overflow.clientWidth, 'desktop has horizontal overflow');

    const desktopReviewScreenshot = path.join(tmpRoot, 'portal-desktop-review.png');
    await desktop.screenshot({ path: desktopReviewScreenshot, fullPage: true });
    const desktopReviewStats = await screenshotStats(desktopReviewScreenshot);
    const desktopReviewArtifact = saveVisualArtifact(
      visualArtifactDir,
      desktopReviewScreenshot,
      'portal-desktop-review.png',
    );
    assertVisualBaseline('desktop review', desktopReviewStats, {
      minWidth: 1200,
      minHeight: 900,
      minColorBuckets: 24,
      minSaturatedRatio: 0.04,
      minDarkRatio: 0.03,
      maxBrightRatio: 0.86,
      minMeanLuma: 20,
      maxMeanLuma: 220,
    });

    await desktop.evaluate(() => setPortalMode('teach'));
    await desktop.waitForFunction(() => !document.querySelector('#portal-mode-teach').hidden);
    const desktopTeachScreenshot = path.join(tmpRoot, 'portal-desktop-teach.png');
    await desktop.screenshot({ path: desktopTeachScreenshot, fullPage: true });
    const desktopTeachStats = await screenshotStats(desktopTeachScreenshot);
    const desktopTeachArtifact = saveVisualArtifact(
      visualArtifactDir,
      desktopTeachScreenshot,
      'portal-desktop-teach.png',
    );
    assertVisualBaseline('desktop teach', desktopTeachStats, {
      minWidth: 1200,
      minHeight: 900,
      minColorBuckets: 24,
      minSaturatedRatio: 0.015,
      minDarkRatio: 0.03,
      maxBrightRatio: 0.86,
      minMeanLuma: 20,
      maxMeanLuma: 220,
    });

    const mobile = await browser.newPage();
    mobile.on('pageerror', (error) => errors.push(`mobile pageerror: ${error.message}`));
    mobile.on('console', (msg) => {
      if (['error', 'warning'].includes(msg.type())) errors.push(`mobile console ${msg.type()}: ${msg.text()}`);
    });
    await mobile.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true });
    await mobile.goto(url, { waitUntil: 'networkidle0' });
    await mobile.waitForSelector('.card', { timeout: 5000 });

    const mobileState = await mobile.evaluate(async () => {
      const firstCard = document.querySelector('.card');
      const initialRect = firstCard.getBoundingClientRect();
      firstCard.scrollIntoView({ block: 'center' });
      await new Promise((resolve, reject) => {
        const started = Date.now();
        const tick = () => {
          const images = Array.from(document.querySelectorAll('.card img'));
          const loaded = images.every((img) => img.naturalWidth > 0);
          if (loaded) resolve();
          else if (Date.now() - started > 5000) reject(new Error('mobile images did not load after scroll'));
          else requestAnimationFrame(tick);
        };
        tick();
      });
      const rect = firstCard.getBoundingClientRect();
      return {
        activeMode: document.querySelector('.portal-mode-btn.active')?.dataset.modeTarget || '',
        cards: document.querySelectorAll('.card').length,
        loadedImages: Array.from(document.querySelectorAll('.card img')).filter((img) => img.naturalWidth > 0).length,
        imageNaturalWidths: Array.from(document.querySelectorAll('.card img')).map((img) => img.naturalWidth),
        firstCardInitialY: Math.round(initialRect.y),
        firstCardRect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
        overflow: {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          bodyScrollWidth: document.body.scrollWidth,
        },
      };
    });

    assert(mobileState.activeMode === 'review', `expected mobile review mode by default, got ${mobileState.activeMode}`);
    assert(mobileState.firstCardInitialY < 900, `mobile review cards start too low: ${mobileState.firstCardInitialY}`);
    assert(mobileState.cards === 2, `expected two mobile cards, got ${mobileState.cards}`);
    assert(mobileState.loadedImages === 2, `expected two loaded mobile images, got ${mobileState.loadedImages}`);
    assert(mobileState.overflow.scrollWidth <= mobileState.overflow.clientWidth, 'mobile has horizontal overflow');

    const mobileScreenshot = path.join(tmpRoot, 'portal-mobile.png');
    await mobile.screenshot({ path: mobileScreenshot, fullPage: false });
    const mobileStats = await screenshotStats(mobileScreenshot);
    const mobileArtifact = saveVisualArtifact(
      visualArtifactDir,
      mobileScreenshot,
      'portal-mobile-review.png',
    );
    assertVisualBaseline('mobile', mobileStats, {
      minWidth: 390,
      minHeight: 800,
      minColorBuckets: 18,
      minSaturatedRatio: 0.03,
      minDarkRatio: 0.03,
      maxBrightRatio: 0.9,
      minMeanLuma: 20,
      maxMeanLuma: 230,
    });

    assert(errors.length === 0, `browser console/page errors:\n${errors.join('\n')}`);

    console.log(JSON.stringify({
      ok: true,
      url,
      fixture: {
        output_root: outputRoot,
        project,
        run_id: path.basename(runDir),
      },
      desktop: desktopState,
      mobile: mobileState,
      screenshots: {
        desktopReview: desktopReviewStats,
        desktopTeach: desktopTeachStats,
        mobile: mobileStats,
      },
      visual_artifacts: visualArtifactDir ? {
        directory: visualArtifactDir,
        files: {
          desktopReview: desktopReviewArtifact,
          desktopTeach: desktopTeachArtifact,
          mobile: mobileArtifact,
        },
      } : null,
      server_output: serverOutput.split('\n').filter(Boolean).slice(0, 6),
    }, null, 2));
  } finally {
    if (browser) await browser.close().catch(() => {});
    if (server && server.exitCode === null) {
      server.kill('SIGTERM');
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (server.exitCode === null) server.kill('SIGKILL');
          resolve();
        }, 1500);
        server.once('exit', () => {
          clearTimeout(timeout);
          resolve();
        });
      });
    }
    if (!keepTmp) {
      fs.rmSync(tmpRoot, { recursive: true, force: true });
    } else {
      console.error(`Kept E2E temp dir: ${tmpRoot}`);
    }
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
