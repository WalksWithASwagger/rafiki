#!/usr/bin/env node

/**
 * Rafiki — image generation CLI
 *
 * Supports:
 * - AI image generation via Python / Gemini / OpenAI
 * - HTML-to-image rendering via Puppeteer
 *
 * Usage:
 *   npx rafiki ./article/image-prompts.md
 *   npx rafiki --render ./graphics/hero.html
 *   (bin alias: npx image-gen …)
 */

// Load environment variables from .env file
require('dotenv').config({ quiet: true });

const { Command } = require('commander');
const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Prefer ./.venv so `npx rafiki` works on PEP 668–managed Pythons.
 */
function getPythonExecutable() {
  const root = __dirname;
  const winVenv = path.join(root, '.venv', 'Scripts', 'python.exe');
  const unixVenv = path.join(root, '.venv', 'bin', 'python3');
  if (process.platform === 'win32' && fs.existsSync(winVenv)) {
    return winVenv;
  }
  if (fs.existsSync(unixVenv)) {
    return unixVenv;
  }
  return 'python3';
}

// Dynamic import for chalk (ESM)
let chalk;
async function loadChalk() {
  if (!chalk) {
    chalk = (await import('chalk')).default;
  }
  return chalk;
}

/**
 * Chrome/Chromium for Puppeteer HTML rendering.
 * @see docs/CHROME-PUPPETEER.md
 */
function resolveChromeExecutablePath() {
  const candidates = [
    process.env.PUPPETEER_EXECUTABLE_PATH,
    process.env.CHROME_PATH,
    process.env.GOOGLE_CHROME_BIN,
  ].filter(Boolean);

  for (const p of candidates) {
    if (fs.existsSync(p)) {
      return p;
    }
  }

  const macChrome =
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (fs.existsSync(macChrome)) {
    return macChrome;
  }

  const linuxPaths = [
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
  ];
  for (const p of linuxPaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }

  return undefined;
}

async function runDoctor(c) {
  const pythonBin = getPythonExecutable();
  const pythonVersion = spawnSync(pythonBin, ['--version'], { encoding: 'utf8' });
  const pythonOk = pythonVersion.status === 0;

  const pythonDeps = pythonOk
    ? spawnSync(
        pythonBin,
        [
          '-c',
          [
            'import importlib, json',
            'checks = [',
            '  ("google.genai", "google-genai"),',
            '  ("openai", "openai"),',
            '  ("PIL", "pillow"),',
            '  ("yaml", "pyyaml"),',
            ']',
            'missing = []',
            'for module_name, package_name in checks:',
            '  try:',
            '    importlib.import_module(module_name)',
            '  except Exception:',
            '    missing.append(package_name)',
            'print(json.dumps({"missing": missing}))',
          ].join('\n'),
        ],
        { encoding: 'utf8' }
      )
    : null;

  let missingPythonDeps = [];
  if (pythonDeps && pythonDeps.status === 0) {
    try {
      const parsed = JSON.parse(pythonDeps.stdout || '{}');
      missingPythonDeps = parsed.missing || [];
    } catch (err) {
      missingPythonDeps = ['unable-to-parse'];
    }
  }

  const hasGoogleKey = Boolean(process.env.GOOGLE_API_KEY);
  const hasOpenAIKey = Boolean(process.env.OPENAI_API_KEY);
  const chromeExecutablePath = resolveChromeExecutablePath();
  const envFilePath = path.join(__dirname, '.env');
  const envFileExists = fs.existsSync(envFilePath);
  const criticalIssues = !pythonOk || missingPythonDeps.length > 0 || (!hasGoogleKey && !hasOpenAIKey);

  const statusLine = (ok, label, detail) => {
    const badge = ok ? c.green('[ok]') : c.red('[missing]');
    console.log(`${badge} ${label}: ${detail}`);
  };

  console.log(c.cyan('Rafiki doctor'));
  console.log(c.gray(`  repo: ${__dirname}`));

  statusLine(true, 'Node.js', process.version);
  statusLine(pythonOk, 'Python', pythonOk ? (pythonVersion.stdout || pythonVersion.stderr).trim() : pythonVersion.error?.message || 'not available');
  statusLine(
    missingPythonDeps.length === 0,
    'Python deps',
    missingPythonDeps.length === 0 ? 'requirements installed' : `missing ${missingPythonDeps.join(', ')}`
  );
  statusLine(envFileExists, '.env file', envFileExists ? envFilePath : 'optional but not present');
  statusLine(hasGoogleKey, 'GOOGLE_API_KEY', hasGoogleKey ? 'set' : 'not set');
  statusLine(hasOpenAIKey, 'OPENAI_API_KEY', hasOpenAIKey ? 'set' : 'not set');
  statusLine(Boolean(chromeExecutablePath), 'Chrome/Chromium', chromeExecutablePath || 'will rely on Puppeteer defaults');

  if (criticalIssues) {
    console.log('');
    console.log(c.yellow('Suggested next steps:'));
    if (!pythonOk) {
      console.log('  - Install Python 3 and ensure `python3` is on your PATH, or create `.venv` in the repo root.');
    }
    if (missingPythonDeps.length > 0) {
      console.log('  - Install Python dependencies: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`');
    }
    if (!hasGoogleKey && !hasOpenAIKey) {
      console.log('  - Add at least one provider key in `.env` or your shell environment.');
    }
  }

  process.exit(criticalIssues ? 1 : 0);
}

const program = new Command();

program
  .name('rafiki')
  .description('Rafiki — local-first AI image generation or Puppeteer (HTML→PNG)')
  .version('1.1.0');

// AI Generation command (default)
program
  .argument('[prompts-file]', 'Path to image-prompts.md file')
  .option('-p, --prompt <text>', 'Single text prompt')
  .option('-o, --output <path>', 'Output file path', 'output.png')
  .option('-d, --output-dir <path>', 'Output directory for batch')
  .option('-m, --model <model>', 'Model to use (gemini-2.5-flash-image, gpt-image-2, dall-e-3, …)', 'gemini-2.5-flash-image')
  .option('-a, --aspect-ratio <ratio>', 'Aspect ratio', '16:9')
  .option('-r, --resolution <res>', 'Resolution hint for Gemini Pro (1K, 2K, 4K)', '1K')
  .option('-q, --quality <level>', 'Quality for OpenAI models: low | medium | high', 'high')
  .option('-s, --style <name>', 'Style to apply (kk, hopecode, bcai, or none)')
  .option('--no-style', 'Skip style suffix (same as --style=none)')
  .option('--list-styles', 'Show available styles')
  .option('--reference-image <path>', 'Path to reference image for style guidance')
  .option('--ref <path>', 'Alias for --reference-image')
  .option(
    '--reference-images <csv>',
    'Batch: comma-separated ref paths (one per prompt, or one path for all)'
  )
  .option(
    '--reference-role <mode>',
    'style (default) or mockup — mockup keeps garment photos and adds the print',
    'style'
  )
  .option(
    '--composition-references <csv>',
    'Mockup: comma-separated print-art refs after the garment photo'
  )
  .option('--dry-run', 'Preview without generating')
  .option('--no-viewer', 'Skip generating viewer.html after batch runs')
  .option('--json', 'Emit JSON result to stdout; progress to stderr (agent/pipeline use)')
  .option('--render <html>', 'Render HTML file to image')
  .option('--render-dir <dir>', 'Render all HTML files in directory')
  .option('--usage', 'Show usage statistics')
  .option('--doctor', 'Check Python, dependencies, keys, and Chrome availability')
  .action(async (promptsFile, options) => {
    const c = await loadChalk();

    if (options.doctor) {
      await runDoctor(c);
      return;
    }

    // HTML Rendering mode
    if (options.render || options.renderDir) {
      await handleHtmlRendering(options, c);
      return;
    }

    // AI Generation mode - delegate to Python
    const args = buildPythonArgs(promptsFile, options);

    console.log(c.cyan('Rafiki — running image generator...'));

    const pythonScript = path.join(__dirname, 'generate.py');
    const pythonBin = getPythonExecutable();
    const proc = spawn(pythonBin, [pythonScript, ...args], {
      stdio: 'inherit',
      env: process.env
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        console.log(c.red(`Process exited with code ${code}`));
      }
      process.exit(code);
    });

    proc.on('error', (err) => {
      console.log(c.red(`Failed to start Python: ${err.message}`));
      console.log(
        c.yellow(
          'Create .venv and install deps: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt'
        )
      );
      process.exit(1);
    });
  });

function buildPythonArgs(promptsFile, options) {
  const args = [];

  if (promptsFile) {
    args.push('--prompt-file', promptsFile);
  }

  if (options.prompt) {
    args.push('--prompt', options.prompt);
  }

  if (options.output) {
    args.push('--output', options.output);
  }

  if (options.outputDir) {
    args.push('--output-dir', options.outputDir);
  }

  if (options.model) {
    args.push('--model', options.model);
  }

  if (options.aspectRatio) {
    args.push('--aspect-ratio', options.aspectRatio);
  }

  if (options.resolution) {
    args.push('--resolution', options.resolution);
  }

  if (options.quality) {
    args.push('--quality', options.quality);
  }

  if (options.listStyles) {
    args.push('--list-styles');
  }

  // Commander sets `style: false` when --no-style is used (not a `noStyle` key).
  if (options.style === false || options.noStyle) {
    args.push('--style', 'none');
  } else if (options.style) {
    args.push('--style', options.style);
  }

  if (options.dryRun) {
    args.push('--dry-run');
  }

  // Commander sets viewer: false when --no-viewer is passed
  if (options.viewer === false) {
    args.push('--no-viewer');
  }

  if (options.json) {
    args.push('--json');
  }

  if (options.usage) {
    args.push('--usage');
  }

  if (options.referenceImages) {
    args.push('--reference-images', options.referenceImages);
  } else if (options.referenceImage || options.ref) {
    args.push('--reference-image', options.referenceImage || options.ref);
  }

  if (options.referenceRole && options.referenceRole !== 'style') {
    args.push('--reference-role', options.referenceRole);
  }

  if (options.compositionReferences) {
    args.push('--composition-references', options.compositionReferences);
  }

  return args;
}

async function handleHtmlRendering(options, c) {
  let puppeteer;
  let sharp;

  try {
    puppeteer = require('puppeteer');
    sharp = require('sharp');
  } catch (e) {
    console.log(c.red('Missing dependencies. Run: npm install puppeteer sharp'));
    process.exit(1);
  }

  const files = [];

  if (options.render) {
    files.push(options.render);
  }

  if (options.renderDir) {
    const dir = options.renderDir;
    if (fs.existsSync(dir)) {
      const htmlFiles = fs.readdirSync(dir)
        .filter(f => f.endsWith('.html'))
        .map(f => path.join(dir, f));
      files.push(...htmlFiles);
    }
  }

  if (files.length === 0) {
    console.log(c.red('No HTML files found to render'));
    process.exit(1);
  }

  console.log(c.cyan(`Rendering ${files.length} HTML file(s) to PNG...`));

  const chromeExecutablePath = resolveChromeExecutablePath();
  console.log(
    c.gray(
      `  Chrome: ${chromeExecutablePath || 'Puppeteer bundled Chromium'}`
    )
  );

  const browser = await puppeteer.launch({
    headless: true,
    executablePath: chromeExecutablePath,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    for (const htmlPath of files) {
      const outputPath = htmlPath.replace('.html', '.png');
      console.log(c.gray(`  ${path.basename(htmlPath)} -> ${path.basename(outputPath)}`));

      const page = await browser.newPage();
      await page.setViewport({ width: 1200, height: 630 });

      const absolutePath = path.resolve(htmlPath);
      await page.goto(`file://${absolutePath}`, { waitUntil: 'networkidle0' });

      // Wait for fonts to load
      await page.evaluate(() => document.fonts.ready);

      // Take screenshot
      const screenshot = await page.screenshot({ type: 'png' });

      // Optimize with Sharp
      await sharp(screenshot)
        .png({ quality: 90, compressionLevel: 9 })
        .toFile(outputPath);

      await page.close();
    }

    console.log(c.green(`\nRendered ${files.length} images successfully!`));
  } finally {
    await browser.close();
  }
}

program.parse();
