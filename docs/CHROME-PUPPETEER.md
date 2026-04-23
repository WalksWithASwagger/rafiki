# Chrome / Chromium for HTML rendering (`--render`)

The CLI uses Puppeteer to open local HTML files and screenshot them as PNG. Puppeteer needs a **Chrome or Chromium** binary.

## Resolution order

`index.js` picks `executablePath` in this order:

1. **`PUPPETEER_EXECUTABLE_PATH`** (Puppeteer’s standard env var)
2. **`CHROME_PATH`** or **`GOOGLE_CHROME_BIN`** (common on Linux CI images)
3. **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` if it exists
4. **Linux**: first existing path among `/usr/bin/google-chrome-stable`, `/usr/bin/chromium`, `/usr/bin/chromium-browser`
5. **Omitted** — Puppeteer uses its **bundled Chromium** (works headless in many environments; may need extra Debian packages such as `libnss3`).

## Recommendations

| Environment | Suggestion |
|-------------|------------|
| macOS dev | Install Google Chrome, or set `PUPPETEER_EXECUTABLE_PATH` to your Chromium |
| Linux server / Docker | Install `google-chrome-stable` or `chromium`, set `PUPPETEER_EXECUTABLE_PATH`, or rely on bundled Chromium and install [Puppeteer system deps](https://pptr.dev/guides/docker) |
| CI (GitHub Actions) | Use `browser-actions/setup-chrome` or install `chromium` and export `PUPPETEER_EXECUTABLE_PATH` |

## Sandbox

Launch uses `--no-sandbox` / `--disable-setuid-sandbox` for compatibility in containers. Tighten for your threat model if you only run trusted local HTML.
