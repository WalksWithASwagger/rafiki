"""Build the fixed offline lesson and its still; no provider or server needed."""
import argparse
import hashlib
import html
import json
import math
import re
import subprocess
from pathlib import Path

from sky import Sky

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
PROFILE = SKILL / "profiles/looks-right.json"
NAMES = ("Polaris", "Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar",
         "Alkaid", "Betelgeuse", "Bellatrix", "Rigel", "Saiph")
HOURS = range(3, 8)
ART = ((100, 100), (140, 190), (185, 220), (230, 175), (270, 200), (315, 145),
       (350, 165), (410, 120), (150, 315), (230, 290), (320, 330), (375, 285))


def project(alt, az):
    radius = (90 - alt) / 90 * 200
    return 260 + radius * math.sin(math.radians(az)), 260 - radius * math.cos(math.radians(az))


def chart(hour=4, constructed=False, marked=False):
    points = []
    sky = Sky((2026, 10, 29, hour, 0, 0), 49.2827, -123.1207)
    for name, artwork in zip(NAMES, ART):
        alt, az = sky.alt_az(name)
        if constructed or alt >= 0:
            x, y = artwork if constructed else project(alt, az)
            ring = ' class="correction"' if marked and name in NAMES[-4:] else ''
            points.append(f'<circle data-star="{name}" data-alt="{alt:.8f}" cx="{x:.3f}" '
                          f'cy="{y:.3f}" r="4"{ring}><title>{name}: {alt:.1f}° / {az:.1f}°</title></circle>')
    grid = ''.join(f'<circle class="grid" cx="260" cy="260" r="{r}"/>' for r in (67, 133, 200))
    return ('<svg viewBox="0 0 520 520" role="img" aria-label="' +
            ('Constructed star arrangement' if constructed else f'Selected-star horizon diagram, {hour:02}:00 UTC') +
            '"><circle class="sky" cx="260" cy="260" r="240"/>' + grid +
            '<text x="260" y="42">N</text><text x="480" y="266">E</text>' +
            '<text x="260" y="490">S</text><text x="40" y="266">W</text>' +
            '<text x="260" y="265">90°</text><text x="260" y="465">0°</text>' + ''.join(points) + '</svg>')


def pages(raw):
    data = json.loads(raw)
    expected = json.loads(PROFILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.keys() != expected.keys():
        raise ValueError("profile must contain the lesson's documented copy fields")
    moments = data["moments"]
    if (not isinstance(moments, list) or len(moments) != 5 or
            any(not isinstance(m, dict) or set(m) != {"heading", "body"} for m in moments)):
        raise ValueError("profile needs five heading/body moments")
    texts = [v for k, v in data.items() if k != "moments"] + [v for m in moments for v in m.values()]
    if any(not isinstance(v, str) or not v.strip() for v in texts):
        raise ValueError("all copy must be nonempty plain text")
    copy = {k: html.escape(v) for k, v in data.items() if k != "moments"}
    frames = []
    for hour in HOURS:
        label = f'Oct {28 if hour < 7 else 29}, {(hour - 7) % 24:02}:00 PDT / Oct 29, {hour:02}:00 UTC'
        sky = Sky((2026, 10, 29, hour, 0, 0), 49.2827, -123.1207)
        positions = ' · '.join(f'{n}: alt {sky.alt_az(n)[0]:.1f}°, az {sky.alt_az(n)[1]:.1f}°' for n in NAMES)
        frames.append(f'<div class="frame" data-time="{label}"{ " hidden" if hour != 4 else ""}>'
                      f'{chart(hour)}<p>{label}</p><details><summary>{copy["positions"]}</summary>'
                      f'<p>{positions}</p><p>{copy["sources"]}</p></details></div>')
    visuals = [chart(constructed=True), chart(constructed=True), chart(constructed=True, marked=True),
               ''.join(frames), chart() + '<p class="eyebrow">Oct 28, 2026 · 21:00 PDT / Oct 29 · 04:00 UTC</p>']
    visuals[:3] = [f'<p class="poster">{copy["poster"]}</p>{v}' for v in visuals[:3]]
    sections = []
    for i, (moment, visual) in enumerate(zip(moments, visuals)):
        controls = (f'<div class="choices interactive"><button>{copy["publish"]}</button>'
                    f'<button>{copy["review"]}</button></div>') if i == 1 else ''
        if i == 3:
            controls = f'<label class="interactive">{copy["time"]}<input id="time" type="range" min="0" max="4" value="1" step="1"></label>'
        sections.append(f'<section id="moment-{i}"><div class="words"><p class="eyebrow">0{i + 1} / 05</p>'
                        f'<h2 tabindex="-1">{html.escape(moment["heading"])}</h2><p>{html.escape(moment["body"])}</p>'
                        f'{controls}</div><div class="visual">{visual}</div></section>')
    template = (SKILL / "templates/lesson.html").read_text(encoding="utf-8")
    values = {**copy, "sections": ''.join(sections), "hash": hashlib.sha256(raw).hexdigest()}
    # One substitution pass keeps literal author text from becoming template syntax.
    lesson = re.sub(r'@@(\w+)@@', lambda m: values[m[1]], template)
    return lesson, lesson.replace('<body>', '<body class="still">')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=PROFILE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        lesson, still = pages(args.profile.read_bytes())
        args.output.mkdir()
        for name, content in (("lesson.html", lesson), ("still.html", still)):
            (args.output / name).write_text(content, encoding="utf-8")
        subprocess.run(["node", str(ROOT / "index.js"), "--render", str(args.output / "still.html")], check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Lesson build failed: {error}\n")


if __name__ == "__main__":
    main()
