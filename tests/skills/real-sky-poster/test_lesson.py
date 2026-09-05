import csv
import json
import math
import runpy
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".agents/skills/real-sky-poster/scripts"))
import lesson  # noqa: E402
from sky import Sky  # noqa: E402


def test_incorrect_astronomy_fails_both_entry_points(monkeypatch):
    path = Path(__file__).with_name("test_sky.py")
    gates = runpy.run_path(str(path))
    monkeypatch.setattr(Sky, "alt_az", lambda *args: (0, 0))
    with pytest.raises(AssertionError):
        gates["test_polaris_altitude_equals_latitude"]()
    code = f"import sys,runpy;sys.path.insert(0,{str(lesson.SKILL / 'scripts')!r});from sky import Sky;Sky.alt_az=lambda *a:(0,0);runpy.run_path({str(path)!r},run_name='__main__')"
    assert subprocess.run([sys.executable, "-c", code], capture_output=True).returncode != 0


def test_independent_reference_and_horizon():
    def direction(alt, az):
        a, z = map(math.radians, (alt, az))
        return math.cos(a) * math.cos(z), math.cos(a) * math.sin(z), math.sin(a)
    fixture = Path(__file__).with_name("fixtures") / "reference-sky.csv"
    rows = list(csv.DictReader(line for line in fixture.read_text().splitlines() if not line.startswith('#')))
    assert {(int(r['hour']), r['name']) for r in rows} == {(h, n) for h in lesson.HOURS for n in lesson.NAMES}
    for row in rows:
        alt, az = Sky((2026, 10, 29, int(row['hour']), 0, 0), 49.2827, -123.1207).alt_az(row['name'])
        reference = float(row['alt']), float(row['az'])
        assert math.dist(direction(alt, az), direction(*reference)) < 2 * math.sin(math.radians(0.5))
        assert (alt >= 0) == (reference[0] >= 0)
    sky = Sky((2026, 10, 29, 0, 0, 0), 49.2827, -123.1207)
    assert sky.is_up('Perseus') and sky.alt_az('zet Per')[0] < 0
    assert lesson.project(0, 90) == pytest.approx((460, 260))
    assert lesson.project(90, 0) == pytest.approx((260, 260))
    for hour in lesson.HOURS:
        stars = ElementTree.fromstring(lesson.chart(hour)).findall('./circle[@data-star]')
        expected = {n for n in lesson.NAMES if Sky((2026, 10, 29, hour, 0, 0), 49.2827, -123.1207).alt_az(n)[0] >= 0}
        assert {s.attrib['data-star'] for s in stars} == expected
        assert all(math.hypot(float(s.attrib['cx']) - 260, float(s.attrib['cy']) - 260) <= 200.001 for s in stars)


def test_copy_escaping_and_determinism():
    raw = lesson.PROFILE.read_bytes()
    assert lesson.pages(raw) == lesson.pages(raw)
    data = json.loads(raw)
    data['title'] = '</script><img src="https://invalid.example"> @@hash@@'
    for page in lesson.pages(json.dumps(data).encode()):
        assert '&lt;/script&gt;&lt;img' in page and '@@hash@@' in page
        assert '<img src=' not in page
    for invalid in (b'{}', b'[]', b'invalid', json.dumps({**data, 'moments': []}).encode()):
        with pytest.raises(ValueError):
            lesson.pages(invalid)


def test_build_and_browser(tmp_path):
    out = tmp_path / 'moved lesson with spaces'
    command = [sys.executable, str(lesson.SKILL / 'scripts/lesson.py'), '--output', str(out)]
    assert subprocess.run(command + ['--profile', str(tmp_path / 'missing.json')], capture_output=True).returncode != 0
    assert not out.exists()
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert before == {p.name: p.read_bytes() for p in out.iterdir()}
    import struct
    assert struct.unpack('>II', before['still.png'][16:24]) == (1200, 630)
    portable = tmp_path / 'relocated copy.html'
    portable.write_bytes(before['lesson.html'])
    result = subprocess.run(['node', '-e', BROWSER, str(portable)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


BROWSER = r"""
const assert = require('node:assert/strict'), {pathToFileURL} = require('node:url');
(async () => {
  const browser = await require('puppeteer').launch({headless:true, args:['--no-sandbox']});
  try {
    const page = await browser.newPage(), requests = [];
    page.on('request', r => { if (/^https?:/.test(r.url())) requests.push(r.url()); });
    await page.setOfflineMode(true);
    await page.goto(pathToFileURL(process.argv[1]).href);
    await page.click('#next'); await page.click('.choices button');
    assert.equal(await page.$eval('#progress', el => el.textContent), '3 / 5');
    await page.keyboard.press('ArrowRight'); await page.click('#time');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'time');
    for (const key of ['Home','ArrowRight','ArrowRight','ArrowRight','ArrowRight']) {
      await page.keyboard.press(key);
      assert.equal(await page.$eval('#progress', el => el.textContent), '4 / 5');
      assert.equal(await page.$$eval('.frame', els => els.filter(el => !el.hidden).length), 1);
    }
    assert.match(await page.$eval('#time', el => el.getAttribute('aria-valuetext')), /07:00 UTC/);
    for (const [width,height] of [[390,844],[1440,900],[720,450]]) {
      await page.setViewport({width,height});
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    await page.emulateMediaFeatures([{name:'prefers-reduced-motion', value:'reduce'}]);
    assert.equal(await page.$eval('#next', el => getComputedStyle(el).transitionDuration), '0s');
    await page.setJavaScriptEnabled(false); await page.reload();
    assert.equal(await page.$$eval('section', els => els.filter(el => getComputedStyle(el).display !== 'none').length), 5);
    assert.equal(requests.length, 0);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
"""
