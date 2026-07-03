#!/usr/bin/env node

import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');
const baselineManifestPath = path.join(repoRoot, 'docs', 'portal-visual-baselines.json');
let puppeteer = null;
let sharp = null;

const visualCaptures = {
  desktopReview: {
    id: 'desktop-review',
    label: 'desktop review',
    fileName: 'portal-desktop-review.png',
  },
  desktopTeach: {
    id: 'desktop-teach',
    label: 'desktop teach',
    fileName: 'portal-desktop-teach.png',
  },
  mobileReview: {
    id: 'mobile-review',
    label: 'mobile review',
    fileName: 'portal-mobile-review.png',
  },
};

function parseArgs(argv) {
  const options = {
    visualBaselineMode: 'off',
    selfTestBaselines: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--self-test-baselines') {
      options.selfTestBaselines = true;
      continue;
    }
    if (arg === '--baseline-check') {
      options.visualBaselineMode = 'check';
      continue;
    }
    if (arg === '--baseline-refresh') {
      options.visualBaselineMode = 'refresh';
      continue;
    }
    if (arg === '--visual-baseline') {
      const value = argv[index + 1];
      if (!value) throw new Error('--visual-baseline requires review, check, refresh, or off');
      options.visualBaselineMode = value;
      index += 1;
      continue;
    }
    if (arg.startsWith('--visual-baseline=')) {
      options.visualBaselineMode = arg.slice('--visual-baseline='.length);
      continue;
    }
    throw new Error(`Unknown portal E2E option: ${arg}`);
  }

  if (!['off', 'review', 'check', 'refresh'].includes(options.visualBaselineMode)) {
    throw new Error(`Unsupported --visual-baseline mode: ${options.visualBaselineMode}`);
  }
  return options;
}

function commandWorks(command) {
  const result = spawnSync(command, ['--version'], { encoding: 'utf8' });
  return result.status === 0;
}

async function loadBrowserDeps() {
  if (puppeteer && sharp) return;
  ({ default: puppeteer } = await import('puppeteer'));
  ({ default: sharp } = await import('sharp'));
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

function getBrowserExecutable() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  const candidates = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
  ];
  return candidates.find((candidate) => fs.existsSync(candidate));
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

async function waitForCondition(check, label, timeoutMs = 5000) {
  const startedAt = Date.now();
  let lastError = null;
  while (Date.now() - startedAt < timeoutMs) {
    try {
      if (await check()) return;
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 150));
  }
  throw new Error(`${label} did not become true${lastError ? `: ${lastError.message}` : ''}`);
}

async function setFieldValue(page, selector, value) {
  await page.waitForSelector(selector);
  await page.$eval(selector, (element, nextValue) => {
    const prototype = element.tagName === 'TEXTAREA'
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
    descriptor?.set?.call(element, nextValue);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
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

async function readMobileShell(page) {
  return page.evaluate(() => {
    const viewport = { width: window.innerWidth, height: window.innerHeight };
    const main = document.querySelector('main')?.getBoundingClientRect();
    const desktopSidebar = document
      .querySelector('[data-shell-sidebar="desktop"]')
      ?.getBoundingClientRect();
    const mobileNav = document
      .querySelector('[data-shell-mobile-nav]')
      ?.getBoundingClientRect();
    return {
      viewport,
      mainWidth: Math.round(main?.width || 0),
      mainLeft: Math.round(main?.left || 0),
      desktopSidebarWidth: Math.round(desktopSidebar?.width || 0),
      mobileNavVisible: Boolean(
        mobileNav &&
          mobileNav.width >= viewport.width - 2 &&
          mobileNav.top < viewport.height &&
          mobileNav.height > 0,
      ),
    };
  });
}

function assertMobileShellUsable(shell, label) {
  assert(shell.mainWidth >= 360, `${label} mobile main content is too narrow: ${shell.mainWidth}px`);
  assert(shell.mainLeft <= 1, `${label} mobile main content is offset by ${shell.mainLeft}px`);
  assert(shell.desktopSidebarWidth === 0, `${label} desktop sidebar is visible on mobile`);
  assert(shell.mobileNavVisible, `${label} mobile navigation is not visible`);
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

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    throw new Error(`Could not parse visual baseline manifest at ${filePath}: ${error.message}`);
  }
}

function getStatValue(stats, metricPath) {
  return metricPath.split('.').reduce((value, key) => (
    value && Object.hasOwn(value, key) ? value[key] : undefined
  ), stats);
}

function describeRule(rule) {
  const parts = [];
  if (Object.hasOwn(rule, 'equals')) parts.push(`equal ${rule.equals}`);
  if (Object.hasOwn(rule, 'min')) parts.push(`>= ${rule.min}`);
  if (Object.hasOwn(rule, 'max')) parts.push(`<= ${rule.max}`);
  return parts.join(' and ');
}

function compareCaptureToBaseline(capture, stats, manifest, artifactPath) {
  const baseline = manifest.captures?.[capture.id];
  if (!baseline) {
    throw new Error(`Visual baseline manifest is missing capture "${capture.id}" in ${baselineManifestPath}`);
  }
  const failures = [];
  for (const [metricPath, rule] of Object.entries(baseline.metrics || {})) {
    const actual = getStatValue(stats, metricPath);
    if (actual === undefined) {
      failures.push(`${metricPath} is missing from screenshot stats`);
      continue;
    }
    if (Object.hasOwn(rule, 'equals') && actual !== rule.equals) {
      failures.push(`${metricPath} expected ${describeRule(rule)}, got ${actual}`);
    }
    if (Object.hasOwn(rule, 'min') && actual < rule.min) {
      failures.push(`${metricPath} expected ${describeRule(rule)}, got ${actual}`);
    }
    if (Object.hasOwn(rule, 'max') && actual > rule.max) {
      failures.push(`${metricPath} expected ${describeRule(rule)}, got ${actual}`);
    }
  }

  if (failures.length > 0) {
    throw new Error([
      `Visual baseline drift for ${capture.label}.`,
      `Capture: ${capture.id}`,
      `Artifact: ${artifactPath || stats.file}`,
      ...failures.map((failure) => `- ${failure}`),
    ].join('\n'));
  }
}

function metricRulesFromStats(stats, capture) {
  return {
    nonblank: { equals: true },
    width: { min: Math.floor(stats.width * 0.95) },
    height: { min: capture.id === 'mobile-review' ? 800 : 900 },
    'visual.colorBuckets': { min: Math.max(12, Math.floor(stats.visual.colorBuckets * 0.55)) },
    'visual.saturatedRatio': { min: Number(Math.max(0.01, stats.visual.saturatedRatio * 0.45).toFixed(3)) },
    'visual.darkRatio': { min: Number(Math.max(0.01, stats.visual.darkRatio * 0.45).toFixed(3)) },
    'visual.brightRatio': { max: Number(Math.min(0.96, stats.visual.brightRatio + 0.22).toFixed(3)) },
    'visual.meanLuma': {
      min: Number(Math.max(0, stats.visual.meanLuma - 45).toFixed(2)),
      max: Number(Math.min(255, stats.visual.meanLuma + 45).toFixed(2)),
    },
  };
}

function refreshBaselineManifest(captureResults) {
  const captures = {};
  for (const result of captureResults) {
    captures[result.capture.id] = {
      label: result.capture.label,
      artifact: result.capture.fileName,
      metrics: metricRulesFromStats(result.stats, result.capture),
      observed: {
        width: result.stats.width,
        height: result.stats.height,
        visual: result.stats.visual,
      },
    };
  }

  const manifest = {
    schema_version: 1,
    note: 'Reviewed coarse portal visual baselines. These are metric ranges, not pixel-perfect screenshots.',
    refreshed_at: new Date().toISOString(),
    captures,
  };
  fs.writeFileSync(baselineManifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  return manifest;
}

async function captureVisual(page, tmpRoot, artifactDir, capture) {
  const screenshotPath = path.join(tmpRoot, capture.fileName);
  await page.screenshot({ path: screenshotPath, fullPage: capture.id !== 'mobile-review' });
  const stats = await screenshotStats(screenshotPath);
  const artifact = saveVisualArtifact(artifactDir, screenshotPath, capture.fileName);
  return { capture, stats, artifact };
}

function runBaselineSelfTest() {
  const capture = visualCaptures.desktopReview;
  const stats = {
    file: '/tmp/portal-desktop-review.png',
    width: 1440,
    height: 1200,
    nonblank: true,
    visual: {
      meanLuma: 120,
      darkRatio: 0.12,
      brightRatio: 0.3,
      saturatedRatio: 0.2,
      colorBuckets: 40,
    },
  };
  const manifest = {
    captures: {
      [capture.id]: {
        metrics: {
          nonblank: { equals: true },
          width: { min: 1200 },
          'visual.colorBuckets': { min: 20 },
          'visual.meanLuma': { min: 80, max: 160 },
        },
      },
    },
  };
  compareCaptureToBaseline(capture, stats, manifest, '/tmp/artifacts/portal-desktop-review.png');

  let message = '';
  try {
    compareCaptureToBaseline(capture, {
      ...stats,
      visual: { ...stats.visual, colorBuckets: 4 },
    }, manifest, '/tmp/artifacts/portal-desktop-review.png');
  } catch (error) {
    message = error.message;
  }
  assert(message.includes('Visual baseline drift for desktop review.'), 'drift message did not name the capture');
  assert(message.includes('Artifact: /tmp/artifacts/portal-desktop-review.png'), 'drift message did not include the artifact path');
  assert(message.includes('visual.colorBuckets expected >= 20, got 4'), 'drift message did not include the failed metric');
  console.log('portal visual baseline self-test ok');
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTestBaselines) {
    runBaselineSelfTest();
    return;
  }
  await loadBrowserDeps();
  const python = getPythonExecutable();
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'rafiki-portal-e2e-'));
  const visualModeEnabled = options.visualBaselineMode !== 'off';
  const requestedKeepTmp = envIsSet('RAFIKI_E2E_KEEP_TMP');
  const keepTmp = requestedKeepTmp || (visualModeEnabled && !process.env.RAFIKI_E2E_ARTIFACT_DIR?.trim());
  const visualArtifactDir = visualModeEnabled ? resolveVisualArtifactDir(tmpRoot, keepTmp) : null;
  const baselineManifest = options.visualBaselineMode === 'check' ? readJson(baselineManifestPath) : null;
  const visualResults = [];
  const outputRoot = path.join(tmpRoot, 'output');
  const project = 'e2e-showpiece-smoke';
  const projectDir = path.join(outputRoot, project);
  const smokeEnv = {
    ...process.env,
    RAFIKI_DISABLE_EXTRA_OUTPUTS: '1',
    PYTHONUNBUFFERED: '1',
    GOOGLE_API_KEY: '',
    GEMINI_API_KEY: '',
    OPENAI_API_KEY: '',
  };
  const errors = [];
  let server = null;
  let browser = null;

  try {
    fs.mkdirSync(outputRoot, { recursive: true });
    const generatePromptFile = path.join(tmpRoot, 'generate-prompts.md');
    fs.writeFileSync(
      generatePromptFile,
      [
        '## 1. Generate Smoke Hero',
        '**Prompt:**',
        '> A dry-run browser smoke hero image for the Rafiki generate route.',
        '',
        '## 2. Generate Smoke Detail',
        '**Prompt:**',
        '> A dry-run browser smoke detail image for the Rafiki generate route.',
        '',
      ].join('\n'),
      'utf8',
    );
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
    ], { env: smokeEnv });

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
    manifest.images.push({
      ...manifest.images[0],
      name: 'Missing placeholder smoke',
      file: 'missing-placeholder.png',
      prompt: 'Browser smoke missing placeholder record',
      seed: 999999,
      error: '',
    });
    fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

    run(python, ['generate.py', 'library', '--output-dir', outputRoot], { env: smokeEnv });

    const port = await getFreePort();
    const url = `http://127.0.0.1:${port}/`;
    const libraryUrl = `${url}library`;
    server = spawn(python, ['generate.py', 'serve', '--port', String(port), '--output-dir', outputRoot], {
      cwd: repoRoot,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: smokeEnv,
      detached: process.platform !== 'win32',
    });

    let serverOutput = '';
    server.stdout.on('data', (chunk) => { serverOutput += chunk.toString(); });
    server.stderr.on('data', (chunk) => { serverOutput += chunk.toString(); });

    await waitForServer(url, server);
    await waitForCondition(() => serverOutput.includes('Frontend:'), 'portal server frontend status', 10000);
    assert(
      !serverOutput.includes('Frontend:      legacy fallback'),
      `expected React frontend to start, got legacy fallback\n${serverOutput}`,
    );

    const usage = await fetch(`${url}api/usage`).then((response) => response.json());
    assert(usage.archive.projects === 1, `expected one project, got ${usage.archive.projects}`);
    assert(usage.archive.runs === 1, `expected one run, got ${usage.archive.runs}`);
    assert(usage.archive.images === 3, `expected three images, got ${usage.archive.images}`);

    const readiness = await fetch(`${url}api/deploy-readiness`).then((response) => response.json());
    assert(Array.isArray(readiness.checks), 'deploy readiness did not return checks');
    assert(!JSON.stringify(readiness).toLowerCase().includes('secret'), 'deploy readiness leaked a secret-like value');

    browser = await puppeteer.launch({
      headless: 'new',
      executablePath: getBrowserExecutable(),
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const libraryState = await fetch(`${url}api/library-state`).then((response) => response.json());
    assert(libraryState.projects.length === 1, `expected one library project, got ${libraryState.projects.length}`);
    assert(libraryState.runs.length === 1, `expected one library run, got ${libraryState.runs.length}`);
    assert(libraryState.images.length === 3, `expected three library images, got ${libraryState.images.length}`);
    assert(libraryState.health.missingRecords === 1, `expected one missing image, got ${libraryState.health.missingRecords}`);
    assert(libraryState.totals.visible.projects === 1, 'library state visible project total was wrong');
    assert(libraryState.totals.visible.images === 3, 'library state visible image total was wrong');
    assert(libraryState.totals.visible.missing === 1, 'library state visible missing total was wrong');
    assert(Array.isArray(libraryState.sourceWarnings), 'library state did not return source warnings');
    const firstRun = libraryState.runs[0];
    const firstPresent = libraryState.images.find((image) => image.status === 'present');
    const missingRecord = libraryState.images.find((image) => image.status === 'missing');
    assert(firstPresent, 'library state did not include a present image');
    assert(missingRecord, 'library state did not include a missing image');

    const desktop = await browser.newPage();
    desktop.on('pageerror', (error) => errors.push(`desktop pageerror: ${error.message}`));
    desktop.on('console', (msg) => {
      if (['error', 'warning'].includes(msg.type())) errors.push(`desktop console ${msg.type()}: ${msg.text()}`);
    });
    await desktop.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });
    await desktop.goto(libraryUrl, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Projects'));
    await desktop.waitForFunction(() => Array.from(document.querySelectorAll('img[src^="/output/"]')).some((img) => img.naturalWidth > 0));

    const desktopState = await desktop.evaluate(() => ({
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      text: document.body.textContent || '',
      outputImages: Array.from(document.querySelectorAll('img[src^="/output/"]')).map((img) => ({
        src: img.getAttribute('src') || '',
        naturalWidth: img.naturalWidth,
      })),
      routeLinks: Array.from(document.querySelectorAll('a[href]')).map((link) => link.getAttribute('href')),
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        bodyScrollWidth: document.body.scrollWidth,
      },
    }));
    assert(desktopState.title.includes('Library'), `unexpected library title: ${desktopState.title}`);
    assert(desktopState.h1 === 'Projects', `expected Projects heading, got ${desktopState.h1}`);
    assert(desktopState.text.includes(libraryState.projects[0].name), 'library did not render the live project name');
    assert(desktopState.outputImages.some((image) => image.naturalWidth > 0), 'desktop library image did not load from /output');
    assert(desktopState.overflow.scrollWidth <= desktopState.overflow.clientWidth, 'desktop library has horizontal overflow');

    const desktopScreenshot = path.join(tmpRoot, 'portal-desktop-library.png');
    await desktop.screenshot({ path: desktopScreenshot, fullPage: true });
    const desktopScreenshotStats = await screenshotStats(desktopScreenshot);
    assert(desktopScreenshotStats.nonblank, 'desktop library screenshot was blank');

    if (visualModeEnabled) {
      const result = await captureVisual(desktop, tmpRoot, visualArtifactDir, visualCaptures.desktopReview);
      visualResults.push(result);
      if (baselineManifest) compareCaptureToBaseline(result.capture, result.stats, baselineManifest, result.artifact);
    }

    await desktop.goto(`${url}generate`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Image generation'));
    await desktop.waitForSelector('[data-testid="generate-single-prompt"]');
    await desktop.waitForSelector('[data-testid="generate-reference-primary"]');
    await desktop.click('[data-testid="generate-reference-primary"]');
    await setFieldValue(desktop, '[data-testid="generate-project"]', 'e2e-generate-smoke');
    await setFieldValue(
      desktop,
      '[data-testid="generate-single-prompt"]',
      'A dry-run generate smoke image using a saved Rafiki library reference.',
    );
    await desktop.click('[data-testid="generate-submit"]');
    let generateSingleLastState = null;
    try {
      await waitForCondition(async () => {
        const state = await desktop.evaluate(() => ({
          text: document.body.textContent || '',
          result: document.querySelector('[data-testid="generate-result"]')?.textContent || '',
          project: document.querySelector('[data-testid="generate-project"]')?.value || '',
          prompt: document.querySelector('[data-testid="generate-single-prompt"]')?.value || '',
        }));
        generateSingleLastState = {
          ...state,
          text: state.text.slice(0, 900),
          result: state.result.slice(0, 500),
        };
        if (state.text.includes('Single prompt is required')) {
          throw new Error('single prompt was not bound before submit');
        }
        if (state.text.includes('generation failed') || state.text.includes('Generation failed')) {
          throw new Error(state.text.slice(0, 500));
        }
        return state.result.includes('1/1') && state.text.includes('Dry run complete');
      }, 'generate single dry run', 30000);
    } catch (error) {
      throw new Error(`${error.message}: ${JSON.stringify(generateSingleLastState)}`);
    }
    await desktop.click('[data-generate-mode="batch-inline"]');
    const batchPromptSelectors = await desktop.$$('[data-testid="generate-batch-prompt"]');
    assert(batchPromptSelectors.length >= 2, 'generate inline batch prompts were not rendered');
    await batchPromptSelectors[0].evaluate((element) => {
      Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set?.call(
        element,
        'A dry-run inline batch smoke hero.',
      );
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await batchPromptSelectors[1].evaluate((element) => {
      Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set?.call(
        element,
        'A dry-run inline batch smoke detail.',
      );
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await desktop.click('[data-testid="generate-submit"]');
    await desktop.waitForFunction(() => (
      document.querySelector('[data-testid="generate-result"]')?.textContent?.includes('2/2')
    ));
    await desktop.click('[data-generate-mode="batch-file"]');
    await setFieldValue(desktop, '[data-testid="generate-prompt-file"]', generatePromptFile);
    await desktop.click('[data-testid="generate-preview-prompt-file"]');
    await desktop.waitForFunction(() => document.body.textContent?.includes('2 prompts parsed'));
    const generateState = await desktop.evaluate(() => ({
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      text: document.body.textContent || '',
      selectedReference: Boolean(document.body.textContent?.includes('/output/')),
      resultText: document.querySelector('[data-testid="generate-result"]')?.textContent || '',
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
    }));
    assert(generateState.title.includes('Generate'), `unexpected generate title: ${generateState.title}`);
    assert(generateState.h1 === 'Generate', `expected Generate heading, got ${generateState.h1}`);
    assert(generateState.selectedReference, 'generate route did not select a library reference');
    assert(generateState.resultText.includes('2/2'), 'generate inline batch dry-run did not complete');
    assert(generateState.text.includes('2 prompts parsed'), 'generate prompt-file preview did not render');
    assert(generateState.overflow.scrollWidth <= generateState.overflow.clientWidth, 'desktop generate has horizontal overflow');

    await desktop.goto(`${url}library/${encodeURIComponent(firstRun.id)}`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('File missing'));
    const runState = await desktop.evaluate(() => ({
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      text: document.body.textContent || '',
      viewerLinks: Array.from(document.querySelectorAll('a[href^="/viewer/"]')).length,
      outputImages: Array.from(document.querySelectorAll('img[src^="/output/"]')).map((img) => img.naturalWidth),
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
    }));
    assert(runState.h1 === firstRun.label, `expected run heading ${firstRun.label}, got ${runState.h1}`);
    assert(runState.viewerLinks >= 2, `expected viewer links on run page, got ${runState.viewerLinks}`);
    assert(runState.text.includes('File missing'), 'run page did not show missing image placeholder');
    assert(runState.outputImages.some((width) => width > 0), 'run page present image did not load');
    assert(runState.overflow.scrollWidth <= runState.overflow.clientWidth, 'run page has horizontal overflow');

    await desktop.goto(`${url}viewer/${encodeURIComponent(firstPresent.id)}`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction((name) => document.body.textContent?.includes(name), {}, firstPresent.name);
    const viewerState = await desktop.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const starButton = buttons.find((button) => button.textContent?.includes('Star'));
      const trayButton = buttons.find((button) => button.textContent?.includes('Add to export tray'));
      starButton?.click();
      trayButton?.click();
      return {
        title: document.querySelector('h1')?.textContent?.trim() || '',
        clickedStar: Boolean(starButton),
        clickedTray: Boolean(trayButton),
        imageLoaded: Array.from(document.querySelectorAll('img[src^="/output/"]')).some((img) => img.naturalWidth > 0),
      };
    });
    assert(viewerState.title === firstPresent.name, `viewer title mismatch: ${viewerState.title}`);
    assert(viewerState.clickedStar, 'viewer star button was not found');
    assert(viewerState.clickedTray, 'viewer export tray button was not found');
    assert(viewerState.imageLoaded, 'viewer image did not load from /output');

    await waitForCondition(async () => {
      const ratings = await fetch(`${url}api/ratings`).then((response) => response.json());
      return ratings[firstPresent.key] === 'star';
    }, 'rating write persistence');

    await desktop.goto(`${url}export`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Staged for delivery'));
    const exportState = await desktop.evaluate(() => ({
      text: document.body.textContent || '',
      stagedImages: Array.from(document.querySelectorAll('img[src^="/output/"]')).filter((img) => img.naturalWidth > 0).length,
    }));
    assert(exportState.text.includes('Staged for delivery'), 'export route did not render');
    assert(exportState.stagedImages >= 1, 'export route did not show the staged real image');

    await desktop.goto(`${url}registry`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Asset registry'));
    const registryState = await desktop.evaluate(() => ({
      hasTitle: Boolean(Array.from(document.querySelectorAll('h1')).find((node) => node.textContent?.includes('Asset registry'))),
      hasStatusText: Boolean(document.body.textContent?.includes('indexed')),
    }));
    assert(registryState.hasTitle, 'registry route did not render');

    await desktop.goto(`${url}health`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Advisories'));
    const healthState = await desktop.evaluate(() => ({
      hasMissingAdvisory: Boolean(document.body.textContent?.includes('Missing files')),
      hasManifestCount: Boolean(document.body.textContent?.includes('Manifest images')),
      hasReadOnlyLabel: Boolean(document.body.textContent?.includes('Read-only report')),
      hasQueuedCopy: Boolean(document.body.textContent?.includes('Queued:')),
    }));
    assert(healthState.hasMissingAdvisory, 'health route did not show missing-file advisory');
    assert(healthState.hasReadOnlyLabel, 'health route did not identify itself as read-only');
    assert(!healthState.hasQueuedCopy, 'health route still includes fake queued action copy');

    await desktop.goto(`${url}spend`, { waitUntil: 'networkidle0' });
    await desktop.waitForFunction(() => document.body.textContent?.includes('Cost basis'));
    const currentUsage = await fetch(`${url}api/usage`).then((response) => response.json());
    const expectedSpendImages = String(currentUsage.archive.images);
    const spendState = await desktop.evaluate((expectedImages) => ({
      hasSpend: Boolean(document.body.textContent?.includes('Spend')),
      hasImageCount: Boolean(document.body.textContent?.includes(`Images${expectedImages}`)),
      hasCostBasis: Boolean(document.body.textContent?.includes('Cost basis')),
    }), expectedSpendImages);
    assert(spendState.hasSpend, 'spend route did not render');
    assert(spendState.hasImageCount, 'spend route did not reflect live image count');

    if (visualModeEnabled) {
      const result = await captureVisual(desktop, tmpRoot, visualArtifactDir, visualCaptures.desktopTeach);
      visualResults.push(result);
      if (baselineManifest) compareCaptureToBaseline(result.capture, result.stats, baselineManifest, result.artifact);
    }

    const mobile = await browser.newPage();
    mobile.on('pageerror', (error) => errors.push(`mobile pageerror: ${error.message}`));
    mobile.on('console', (msg) => {
      if (['error', 'warning'].includes(msg.type())) errors.push(`mobile console ${msg.type()}: ${msg.text()}`);
    });
    await mobile.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true });
    await mobile.goto(libraryUrl, { waitUntil: 'networkidle0' });
    await mobile.waitForFunction(() => document.body.textContent?.includes('Projects'));
    await mobile.waitForFunction(() => Array.from(document.querySelectorAll('img[src^="/output/"]')).some((img) => img.naturalWidth > 0));
    const mobileState = await mobile.evaluate(() => ({
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      loadedImages: Array.from(document.querySelectorAll('img[src^="/output/"]')).filter((img) => img.naturalWidth > 0).length,
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        bodyScrollWidth: document.body.scrollWidth,
      },
    }));
    mobileState.shell = await readMobileShell(mobile);
    assert(mobileState.title.includes('Library'), `unexpected mobile title: ${mobileState.title}`);
    assert(mobileState.h1 === 'Projects', `expected mobile Projects heading, got ${mobileState.h1}`);
    assert(mobileState.loadedImages >= 1, 'mobile library image did not load');
    assert(mobileState.overflow.scrollWidth <= mobileState.overflow.clientWidth, 'mobile library has horizontal overflow');
    assertMobileShellUsable(mobileState.shell, 'library');

    const mobileScreenshot = path.join(tmpRoot, 'portal-mobile-library.png');
    await mobile.screenshot({ path: mobileScreenshot, fullPage: true });
    const mobileScreenshotStats = await screenshotStats(mobileScreenshot);
    assert(mobileScreenshotStats.nonblank, 'mobile library screenshot was blank');

    await mobile.goto(`${url}viewer/${encodeURIComponent(firstPresent.id)}`, { waitUntil: 'networkidle0' });
    await mobile.waitForFunction((name) => document.body.textContent?.includes(name), {}, firstPresent.name);
    const mobileViewerState = await mobile.evaluate(() => ({
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      imageLoaded: Array.from(document.querySelectorAll('img[src^="/output/"]')).some((img) => img.naturalWidth > 0),
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
    }));
    mobileViewerState.shell = await readMobileShell(mobile);
    assert(mobileViewerState.h1 === firstPresent.name, `mobile viewer title mismatch: ${mobileViewerState.h1}`);
    assert(mobileViewerState.imageLoaded, 'mobile viewer image did not load from /output');
    assert(mobileViewerState.overflow.scrollWidth <= mobileViewerState.overflow.clientWidth, 'mobile viewer has horizontal overflow');
    assertMobileShellUsable(mobileViewerState.shell, 'viewer');

    const mobileViewerScreenshot = path.join(tmpRoot, 'portal-mobile-viewer.png');
    await mobile.screenshot({ path: mobileViewerScreenshot, fullPage: true });
    const mobileViewerScreenshotStats = await screenshotStats(mobileViewerScreenshot);
    assert(mobileViewerScreenshotStats.nonblank, 'mobile viewer screenshot was blank');

    await mobile.goto(`${url}health`, { waitUntil: 'networkidle0' });
    await mobile.waitForFunction(() => document.body.textContent?.includes('Advisories'));
    const mobileHealthState = await mobile.evaluate(() => ({
      hasReadOnlyLabel: Boolean(document.body.textContent?.includes('Read-only report')),
      hasMissingAdvisory: Boolean(document.body.textContent?.includes('Missing files')),
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
    }));
    mobileHealthState.shell = await readMobileShell(mobile);
    assert(mobileHealthState.hasReadOnlyLabel, 'mobile health did not show read-only label');
    assert(mobileHealthState.hasMissingAdvisory, 'mobile health did not show missing advisory');
    assert(mobileHealthState.overflow.scrollWidth <= mobileHealthState.overflow.clientWidth, 'mobile health has horizontal overflow');
    assertMobileShellUsable(mobileHealthState.shell, 'health');

    const mobileHealthScreenshot = path.join(tmpRoot, 'portal-mobile-health.png');
    await mobile.screenshot({ path: mobileHealthScreenshot, fullPage: true });
    const mobileHealthScreenshotStats = await screenshotStats(mobileHealthScreenshot);
    assert(mobileHealthScreenshotStats.nonblank, 'mobile health screenshot was blank');

    await mobile.goto(`${url}generate`, { waitUntil: 'networkidle0' });
    await mobile.waitForFunction(() => document.body.textContent?.includes('Image generation'));
    const mobileGenerateState = await mobile.evaluate(() => ({
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      hasDryRunBadge: Boolean(document.body.textContent?.includes('Dry-run default')),
      overflow: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
    }));
    mobileGenerateState.shell = await readMobileShell(mobile);
    assert(mobileGenerateState.title.includes('Generate'), `unexpected mobile generate title: ${mobileGenerateState.title}`);
    assert(mobileGenerateState.h1 === 'Generate', `expected mobile Generate heading, got ${mobileGenerateState.h1}`);
    assert(mobileGenerateState.hasDryRunBadge, 'mobile generate did not show dry-run default');
    assert(mobileGenerateState.overflow.scrollWidth <= mobileGenerateState.overflow.clientWidth, 'mobile generate has horizontal overflow');
    assertMobileShellUsable(mobileGenerateState.shell, 'generate');

    const mobileGenerateScreenshot = path.join(tmpRoot, 'portal-mobile-generate.png');
    await mobile.screenshot({ path: mobileGenerateScreenshot, fullPage: true });
    const mobileGenerateScreenshotStats = await screenshotStats(mobileGenerateScreenshot);
    assert(mobileGenerateScreenshotStats.nonblank, 'mobile generate screenshot was blank');

    if (visualModeEnabled) {
      await mobile.goto(libraryUrl, { waitUntil: 'networkidle0' });
      await mobile.waitForFunction(() => document.body.textContent?.includes('Projects'));
      await mobile.waitForFunction(() => Array.from(document.querySelectorAll('img[src^="/output/"]')).some((img) => img.naturalWidth > 0));
      const result = await captureVisual(mobile, tmpRoot, visualArtifactDir, visualCaptures.mobileReview);
      visualResults.push(result);
      if (baselineManifest) compareCaptureToBaseline(result.capture, result.stats, baselineManifest, result.artifact);
    }

    assert(errors.length === 0, `browser console/page errors:\n${errors.join('\n')}`);

    const refreshedManifest = options.visualBaselineMode === 'refresh'
      ? refreshBaselineManifest(visualResults)
      : null;

    console.log(JSON.stringify({
      ok: true,
      url,
      visual_baseline: {
        mode: options.visualBaselineMode,
        manifest: visualModeEnabled ? baselineManifestPath : null,
        refreshed: Boolean(refreshedManifest),
      },
      fixture: {
        output_root: outputRoot,
        project,
        run_id: path.basename(runDir),
      },
      library_state: {
        projects: libraryState.projects.length,
        runs: libraryState.runs.length,
        images: libraryState.images.length,
        missing: libraryState.health.missingRecords,
        rated_key: firstPresent.key,
      },
      desktop: {
        library: desktopState,
        run: runState,
        viewer: viewerState,
        export: exportState,
        registry: registryState,
        health: healthState,
        spend: spendState,
        generate: generateState,
        screenshot: desktopScreenshotStats,
      },
      mobile: mobileState,
      mobile_screenshot: mobileScreenshotStats,
      mobile_viewer: mobileViewerState,
      mobile_viewer_screenshot: mobileViewerScreenshotStats,
      mobile_health: mobileHealthState,
      mobile_health_screenshot: mobileHealthScreenshotStats,
      mobile_generate: mobileGenerateState,
      mobile_generate_screenshot: mobileGenerateScreenshotStats,
      screenshots: visualModeEnabled ? Object.fromEntries(
        visualResults.map((result) => [result.capture.id, result.stats]),
      ) : null,
      visual_artifacts: visualArtifactDir ? {
        directory: visualArtifactDir,
        files: Object.fromEntries(
          visualResults.map((result) => [result.capture.id, result.artifact]),
        ),
      } : null,
      server_output: serverOutput.split('\n').filter(Boolean).slice(0, 6),
    }, null, 2));
  } finally {
    if (browser) await browser.close().catch(() => {});
    if (server && server.exitCode === null) {
      const targetPid = process.platform === 'win32' ? server.pid : -server.pid;
      try {
        process.kill(targetPid, 'SIGTERM');
      } catch {
        server.kill('SIGTERM');
      }
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (server.exitCode === null) {
            try {
              process.kill(targetPid, 'SIGKILL');
            } catch {
              server.kill('SIGKILL');
            }
          }
          resolve();
        }, 1500);
        server.once('exit', () => {
          clearTimeout(timeout);
          resolve();
        });
      });
    }
    server?.stdout?.destroy();
    server?.stderr?.destroy();
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
