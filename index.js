#!/usr/bin/env node

/**
 * Rafiki — image generation CLI
 *
 * Supports:
 * - AI image generation via Python / Gemini (Nano Banana)
 * - HTML-to-image rendering via Puppeteer
 *
 * Usage:
 *   npx rafiki ./article/image-prompts.md
 *   npx rafiki --render ./graphics/hero.html
 *   (bin alias: npx image-gen …)
 */

// Load environment variables from .env file
require('dotenv').config();

const { Command } = require('commander');
const { spawn } = require('child_process');
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

const program = new Command();

program
  .name('rafiki')
  .description('Rafiki — Gemini image generation (Nano Banana) or Puppeteer (HTML→PNG)')
  .version('1.0.0');

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
  .action(async (promptsFile, options) => {
    const c = await loadChalk();

    // HTML Rendering mode
    if (options.render || options.renderDir) {
      await handleHtmlRendering(options, c);
      return;
    }

    // AI Generation mode - delegate to Python
    const args = buildPythonArgs(promptsFile, options);

    console.log(c.cyan('Rafiki — running Nano Banana image generator...'));

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
