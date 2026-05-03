#!/usr/bin/env python3
"""Generate a combined RAP certification viewer with captions and social post copy."""

from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "rap-all-weeks"

WEEK_DIRS = {
    1: SCRIPT_DIR / "output/rap-week-1/run-20260502-204603",
    2: SCRIPT_DIR / "output/rap-week-2/run-20260502-220255",
    3: SCRIPT_DIR / "output/rap-week-3/run-20260502-221030",
    4: SCRIPT_DIR / "output/rap-week-4/run-20260502-221602",
}

WEEK_TITLES = {
    1: "Week 1 — Foundations",
    2: "Week 2 — Core Ethics",
    3: "Week 3 — Societal Impact",
    4: "Week 4 — The Human Element",
}

# fmt: off
RAP_IMAGES = [
    # ── Week 1 ──────────────────────────────────────────────────────────────
    {"week": 1, "slug": "01-data-as-structured-observation",
     "title": "Data as Structured Observation",
     "caption": "Every click, step, and search is a data point. AI begins not with algorithms, but with observation.",
     "social": None},
    {"week": 1, "slug": "02-signal-vs-noise",
     "title": "Signal vs. Noise",
     "caption": "The skill isn't generating more data—it's learning to see the pattern inside the chaos.",
     "social": None},
    {"week": 1, "slug": "03-traditional-programming-vs-machine-learning",
     "title": "Traditional Programming vs. Machine Learning",
     "caption": "Rules written by hand versus patterns grown from examples. Two ways to teach a machine to think.",
     "social": None},
    {"week": 1, "slug": "04-the-neural-network-layers-of-abstraction",
     "title": "The Neural Network",
     "caption": "Layer by layer, simple signals become complex understanding. Depth is the intelligence.",
     "social": None},
    {"week": 1, "slug": "05-the-attention-mechanism-every-word-relates-to-every-other-word",
     "title": "The Attention Mechanism",
     "caption": "Every word in a sentence relates to every other word. The 2017 breakthrough that changed everything.",
     "social": None},
    {"week": 1, "slug": "06-the-hallucination-problem-confident-and-wrong",
     "title": "The Hallucination Problem",
     "caption": "Confident and wrong. The most dangerous AI failure mode isn't silence—it's convincing fiction.",
     "social": "The most dangerous AI failure mode isn't silence—it's confident fiction. When a system is certain and wrong, the forest is dazzled. The compass at its roots points elsewhere.\n\n#ResponsibleAI #AILiteracy #RAP"},
    {"week": 1, "slug": "07-the-react-loop-agents-reason-and-act",
     "title": "The ReAct Loop",
     "caption": "Perceive. Reason. Act. Observe. The continuous cycle that powers agentic AI.",
     "social": None},
    {"week": 1, "slug": "08-the-ai-governance-landscape",
     "title": "The AI Governance Landscape",
     "caption": "No single map covers the territory. Multiple frameworks, overlapping, each marking the same ecosystem differently.",
     "social": None},
    {"week": 1, "slug": "09-what-is-an-ai-shaped-problem",
     "title": "What Is an AI-Shaped Problem?",
     "caption": "Not everything belongs in the machine. Knowing the difference is the first skill.",
     "social": None},
    {"week": 1, "slug": "10-human-in-the-loop-meaningful-oversight",
     "title": "Human in the Loop",
     "caption": "The hand that can close the gap. Meaningful oversight isn't ceremonial—it's structural.",
     "social": "Meaningful AI oversight isn't ceremonial. It's the hand that genuinely can close the gap. Responsible AI Professional — Week 1.\n\n#HumanInTheLoop #AIGovernance #ResponsibleAI"},

    # ── Week 2 ──────────────────────────────────────────────────────────────
    {"week": 2, "slug": "01-algorithmic-bias-the-skewed-scale",
     "title": "Algorithmic Bias",
     "caption": "The scale was tilted long before the algorithm ran. Historical imbalance becomes automated imbalance.",
     "social": "The scale was tilted long before the algorithm ran. Historical imbalance becomes automated imbalance—unless we excavate the roots.\n\n#AIBias #ResponsibleAI #TechEquity"},
    {"week": 2, "slug": "02-conflicting-fairness-definitions",
     "title": "Conflicting Fairness Definitions",
     "caption": "Three clearings, three definitions of fair—each internally coherent, mutually incompatible.",
     "social": None},
    {"week": 2, "slug": "03-hiring-algorithm-bias-the-sorted-seeds",
     "title": "Hiring Algorithm Bias",
     "caption": "Identical seeds, unequal soil. When historical bias is baked into the sorting mechanism itself.",
     "social": None},
    {"week": 2, "slug": "04-privacy-data-consent-the-traced-forest",
     "title": "Privacy & Data Consent",
     "caption": "You left traces you didn't know you left. The forest floor remembers every step.",
     "social": "You left traces you didn't know you left. Every step, timestamped and mapped. Data consent starts with making the invisible visible.\n\n#AIPrivacy #DataConsent #ResponsibleAI"},
    {"week": 2, "slug": "05-surveillance-capitalism-the-watching-canopy",
     "title": "Surveillance Capitalism",
     "caption": "The canopy watches. It's not malicious—it's purposeful. Cataloguing and monetizing every movement.",
     "social": None},
    {"week": 2, "slug": "06-differential-privacy-the-protective-fog",
     "title": "Differential Privacy",
     "caption": "The fog protects individuals without hiding the pattern. Mathematics as a privacy shield.",
     "social": None},
    {"week": 2, "slug": "07-copyright-creative-labor-the-harvested-glow",
     "title": "Copyright & Creative Labor",
     "caption": "The glow was grown slowly, individually, over time. The harvest is instant and systematic.",
     "social": None},
    {"week": 2, "slug": "08-prediction-vs-description-the-twin-paths",
     "title": "Prediction vs. Description",
     "caption": "One path follows what happened. The other cuts toward what should have. They diverge at the fallen tree.",
     "social": None},
    {"week": 2, "slug": "09-bias-audit-the-root-excavation",
     "title": "Bias Audit",
     "caption": "The inequalities don't disappear on their own. They yield only to careful, systematic excavation.",
     "social": None},
    {"week": 2, "slug": "10-ethics-assessment-artifact-the-mapped-ecosystem",
     "title": "Ethics Assessment",
     "caption": "Documentation is practice. The map that makes the invisible visible.",
     "social": None},

    # ── Week 3 ──────────────────────────────────────────────────────────────
    {"week": 3, "slug": "01-deployment-readiness-the-forest-gate",
     "title": "Deployment Readiness",
     "caption": "The gate is half-open. The hand is the governance layer. The question is whether we're ready.",
     "social": None},
    {"week": 3, "slug": "02-high-stakes-domains-three-forest-paths",
     "title": "High-Stakes Domains",
     "caption": "Healthcare. Justice. Employment. Three paths where AI decisions carry life-altering weight.",
     "social": None},
    {"week": 3, "slug": "03-automation-and-job-displacement-the-replaced-roots",
     "title": "Automation & Job Displacement",
     "caption": "The new roots are brighter and more efficient. The old roots are still alive—pushed toward the margins.",
     "social": "The new roots are brighter. More efficient. The old roots are still alive—they've just been pushed toward the margins. The transition is the responsibility.\n\n#FutureOfWork #AI #WorkerRights"},
    {"week": 3, "slug": "04-augmentation-vs-replacement-two-hands",
     "title": "Augmentation vs. Replacement",
     "caption": "Two hands, one flower. Together they do what neither could accomplish alone.",
     "social": "Two hands, one flower—together doing what neither could accomplish alone. The difference between augmentation and replacement is the question of who leads.\n\n#HumanAI #Augmentation #ResponsibleAI"},
    {"week": 3, "slug": "05-environmental-cost-the-underground-heat",
     "title": "Environmental Cost",
     "caption": "The forest floor looks serene. Underground, the heat is enormous and invisible.",
     "social": None},
    {"week": 3, "slug": "06-right-sizing-models-the-proportionate-forest",
     "title": "Right-Sizing AI Models",
     "caption": "The answer isn't the biggest tree. It's the proportionate wildflower—same output, a fraction of the cost.",
     "social": None},
    {"week": 3, "slug": "07-ai-literacy-the-translation-circle",
     "title": "AI Literacy",
     "caption": "The elder translates what the forest is doing into what the community can understand.",
     "social": None},
    {"week": 3, "slug": "08-deployment-checklist-the-marked-forest-path",
     "title": "Deployment Checklist",
     "caption": "Every risk point marked. Every route approved. This is what readiness looks like in practice.",
     "social": None},
    {"week": 3, "slug": "09-worker-surveillance-the-watched-root-network",
     "title": "Worker Surveillance",
     "caption": "The monitoring layer blazes brighter than the workers it watches. Algorithmic management made visible.",
     "social": None},
    {"week": 3, "slug": "10-failure-response-the-contained-fire",
     "title": "Failure Response",
     "caption": "The failure is real. But it is contained. The plan worked. The forest can recover.",
     "social": None},

    # ── Week 4 ──────────────────────────────────────────────────────────────
    {"week": 4, "slug": "01-deepfakes-synthetic-media-the-mirror-forest",
     "title": "Deepfakes & Synthetic Media",
     "caption": "Two clearings separated by a barely visible seam. The copy shows no imperfection. The wrongness is invisible.",
     "social": "Two forest clearings separated by a barely visible seam. The copy is technically more perfect than the original. The wrongness is invisible. This is the deepfake problem.\n\n#Deepfakes #SyntheticMedia #AILiteracy"},
    {"week": 4, "slug": "02-trust-erosion-the-dimming-forest",
     "title": "Trust Erosion",
     "caption": "Not dead. Not diseased. Just uncertain. The glow retreating, the connections fraying.",
     "social": None},
    {"week": 4, "slug": "03-ai-disclosure-provenance-the-marked-tree",
     "title": "AI Disclosure & Provenance",
     "caption": "The mark is not a judgment. It is information. Transparency in the forest costs nothing.",
     "social": None},
    {"week": 4, "slug": "04-parasocial-dynamics-the-companion-light",
     "title": "Parasocial Dynamics",
     "caption": "The figure has begun to turn toward the companion light before looking at anything else.",
     "social": None},
    {"week": 4, "slug": "05-children-ai-the-guided-seedling",
     "title": "Children & AI",
     "caption": "The shapes determine the angle of growth without the seedling knowing to notice.",
     "social": None},
    {"week": 4, "slug": "06-creativity-in-the-age-of-generative-ai-the-choosing-hand",
     "title": "Creativity in the Age of Generative AI",
     "caption": "Infinite perfect alternatives, slightly out of focus. The human keeps choosing. The act of choosing is the art.",
     "social": "Infinite perfect arrangements, slightly out of focus in the background. The human figure keeps choosing. The act of choosing is the art.\n\n#AICreativity #HumanElement #GenerativeAI"},
    {"week": 4, "slug": "07-agency-autonomous-decision-making-the-forked-root",
     "title": "Agency & Autonomous Decision-Making",
     "caption": "The fork is present. The choice is unmade. Who decides—the pattern-logic or the hand above?",
     "social": None},
    {"week": 4, "slug": "08-meaning-when-ai-can-do-the-work-the-tended-clearing",
     "title": "Meaning When AI Does the Work",
     "caption": "The forest no longer needs their hands. The question of what to do with one's hands in a self-tending world.",
     "social": "The forest tends itself now. Beautiful. Efficient. Self-sustaining. The human sits in the center of it, surrounded by flourishing they made possible. The question of what we do next is the most human question of all.\n\n#AIAndMeaning #HumanFlourishing #ResponsibleAI"},
    {"week": 4, "slug": "09-indigenous-knowledge-cultural-dimensions-the-ancient-map",
     "title": "Indigenous Knowledge & Cultural Dimensions",
     "caption": "The ancient map is still accurate. The forest still responds to it. Two systems, partially overlapping, not fully translating.",
     "social": None},
    {"week": 4, "slug": "10-human-flourishing-the-capstone-forest",
     "title": "Human Flourishing",
     "caption": "All four weeks converge here. This is what responsible AI practice looks like when everything comes together.",
     "social": None},
]
# fmt: on


def _image_rel_path(item: dict) -> str:
    week = item["week"]
    run_dir = WEEK_DIRS[week]
    # path relative to output/rap-all-weeks/viewer.html
    rel = run_dir.relative_to(OUTPUT_DIR.parent.parent) / f"{item['slug']}.png"
    return f"../{rel}"


def build_viewer() -> str:
    items_js = json.dumps(
        [
            {
                "week": img["week"],
                "weekLabel": WEEK_TITLES[img["week"]],
                "title": img["title"],
                "caption": img["caption"],
                "social": img["social"],
                "src": _image_rel_path(img),
            }
            for img in RAP_IMAGES
        ],
        indent=2,
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RAP Certification — Visual Library</title>
<style>
  :root {{
    --green: #1E3A2B;
    --gold: #D4A017;
    --gold-light: #e8b93a;
    --bg: #0d1f16;
    --surface: #162b1e;
    --surface2: #1e3a28;
    --text: #e8e4d8;
    --muted: #8a9e8e;
    --radius: 10px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; min-height: 100vh; }}

  /* ── Header ── */
  header {{ background: var(--green); border-bottom: 2px solid var(--gold); padding: 20px 32px; display: flex; align-items: center; gap: 16px; }}
  .logo {{ width: 48px; height: 48px; border: 2.5px solid var(--gold); border-radius: 8px; display: grid; place-items: center; font-size: 22px; color: var(--gold); flex-shrink: 0; }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; color: var(--text); line-height: 1.2; }}
  header p {{ font-size: 0.85rem; color: var(--muted); margin-top: 2px; }}
  .header-right {{ margin-left: auto; font-size: 0.8rem; color: var(--muted); text-align: right; }}
  .header-right strong {{ color: var(--gold); }}

  /* ── Controls ── */
  .controls {{ padding: 20px 32px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; border-bottom: 1px solid #2a3e30; }}
  .tab-group {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .tab {{ padding: 7px 16px; border-radius: 20px; border: 1px solid #2e4a34; background: var(--surface); color: var(--muted); cursor: pointer; font-size: 0.82rem; font-weight: 500; transition: all .15s; }}
  .tab:hover {{ border-color: var(--gold); color: var(--text); }}
  .tab.active {{ background: var(--gold); border-color: var(--gold); color: #0d1f16; font-weight: 700; }}
  .search-wrap {{ margin-left: auto; position: relative; }}
  .search-wrap input {{ background: var(--surface); border: 1px solid #2e4a34; border-radius: 20px; color: var(--text); padding: 7px 16px 7px 36px; font-size: 0.82rem; width: 220px; outline: none; transition: border-color .15s; }}
  .search-wrap input:focus {{ border-color: var(--gold); }}
  .search-wrap::before {{ content: "🔍"; position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 12px; pointer-events: none; }}
  .count {{ font-size: 0.78rem; color: var(--muted); white-space: nowrap; }}

  /* ── Grid ── */
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; padding: 24px 32px 48px; }}

  /* ── Card ── */
  .card {{ background: var(--surface); border-radius: var(--radius); overflow: hidden; border: 1px solid #2a3e30; transition: transform .15s, border-color .15s, box-shadow .15s; cursor: pointer; display: flex; flex-direction: column; }}
  .card:hover {{ transform: translateY(-3px); border-color: var(--gold); box-shadow: 0 8px 24px rgba(0,0,0,.4); }}
  .card-img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; background: #0d1f16; }}
  .card-img.square {{ aspect-ratio: 1/1; }}
  .card-body {{ padding: 14px 16px 16px; flex: 1; display: flex; flex-direction: column; gap: 8px; }}
  .card-meta {{ display: flex; align-items: center; gap: 8px; }}
  .week-badge {{ font-size: 0.68rem; font-weight: 700; letter-spacing: .04em; padding: 3px 8px; border-radius: 10px; background: var(--green); border: 1px solid var(--gold); color: var(--gold); white-space: nowrap; }}
  .social-badge {{ font-size: 0.68rem; font-weight: 700; padding: 3px 8px; border-radius: 10px; background: #2a1a05; border: 1px solid #c98a10; color: #e8a820; white-space: nowrap; }}
  .card-title {{ font-size: 0.95rem; font-weight: 700; color: var(--text); line-height: 1.3; }}
  .card-caption {{ font-size: 0.8rem; color: var(--muted); line-height: 1.5; flex: 1; }}

  /* ── Lightbox ── */
  #lightbox {{ display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(0,0,0,.88); backdrop-filter: blur(6px); align-items: center; justify-content: center; padding: 20px; }}
  #lightbox.open {{ display: flex; }}
  .lb-inner {{ background: var(--surface); border-radius: 14px; border: 1px solid #2e4a34; max-width: 960px; width: 100%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; }}
  .lb-img-wrap {{ position: relative; background: #0a180f; }}
  .lb-img-wrap img {{ width: 100%; max-height: 60vh; object-fit: contain; display: block; }}
  .lb-close {{ position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,.6); border: 1px solid #3a5040; border-radius: 50%; width: 36px; height: 36px; display: grid; place-items: center; cursor: pointer; color: var(--text); font-size: 18px; line-height: 1; transition: background .15s; }}
  .lb-close:hover {{ background: rgba(0,0,0,.9); border-color: var(--gold); }}
  .lb-nav {{ position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,.6); border: 1px solid #3a5040; border-radius: 50%; width: 40px; height: 40px; display: grid; place-items: center; cursor: pointer; color: var(--text); font-size: 20px; transition: background .15s; }}
  .lb-nav:hover {{ background: rgba(0,0,0,.9); border-color: var(--gold); }}
  #lb-prev {{ left: 12px; }}
  #lb-next {{ right: 12px; }}
  .lb-info {{ padding: 20px 24px 24px; display: flex; flex-direction: column; gap: 12px; }}
  .lb-meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .lb-title {{ font-size: 1.2rem; font-weight: 700; color: var(--text); }}
  .lb-caption {{ font-size: 0.9rem; color: var(--muted); line-height: 1.6; }}
  .lb-social {{ background: #1a1005; border: 1px solid #8a5a10; border-radius: 8px; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }}
  .lb-social-label {{ font-size: 0.75rem; font-weight: 700; letter-spacing: .06em; color: #e8a820; text-transform: uppercase; }}
  .lb-social-text {{ font-size: 0.85rem; color: #d4c090; line-height: 1.6; white-space: pre-wrap; }}
  .lb-download {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; cursor: pointer; border: none; transition: all .15s; text-decoration: none; }}
  .btn-gold {{ background: var(--gold); color: #0d1f16; }}
  .btn-gold:hover {{ background: var(--gold-light); }}
  .btn-outline {{ background: transparent; border: 1px solid #2e4a34; color: var(--muted); }}
  .btn-outline:hover {{ border-color: var(--gold); color: var(--text); }}
  .copy-confirm {{ font-size: 0.75rem; color: #6fcf6f; display: none; }}
  .copy-confirm.show {{ display: inline; }}

  /* ── Empty ── */
  .empty {{ grid-column: 1/-1; text-align: center; padding: 60px 20px; color: var(--muted); font-size: 0.95rem; }}

  @media (max-width: 600px) {{
    header {{ padding: 16px 16px; }}
    .controls {{ padding: 14px 16px; }}
    .grid {{ padding: 16px 16px 40px; gap: 14px; }}
    .search-wrap input {{ width: 160px; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo">🌲</div>
  <div>
    <h1>Responsible AI Professional — Visual Library</h1>
    <p>BC + AI Certification Program · 40 images across 4 weeks</p>
  </div>
  <div class="header-right">
    <strong>bcai</strong> style · gpt-image-2<br>
    BC old-growth forest visual language
  </div>
</header>

<div class="controls">
  <div class="tab-group">
    <button class="tab active" data-week="0">All Weeks</button>
    <button class="tab" data-week="1">Week 1 — Foundations</button>
    <button class="tab" data-week="2">Week 2 — Core Ethics</button>
    <button class="tab" data-week="3">Week 3 — Societal Impact</button>
    <button class="tab" data-week="4">Week 4 — Human Element</button>
  </div>
  <span class="count" id="count">40 images</span>
  <div class="search-wrap">
    <input type="text" id="search" placeholder="Search titles & captions…" autocomplete="off">
  </div>
</div>

<div class="grid" id="grid"></div>

<div id="lightbox">
  <div class="lb-inner">
    <div class="lb-img-wrap">
      <img id="lb-img" src="" alt="">
      <button class="lb-close" id="lb-close">×</button>
      <button class="lb-nav" id="lb-prev">‹</button>
      <button class="lb-nav" id="lb-next">›</button>
    </div>
    <div class="lb-info">
      <div class="lb-meta">
        <span class="week-badge" id="lb-week"></span>
        <span class="social-badge" id="lb-social-badge" style="display:none">📣 Social Post</span>
      </div>
      <div class="lb-title" id="lb-title"></div>
      <div class="lb-caption" id="lb-caption"></div>
      <div class="lb-social" id="lb-social-box" style="display:none">
        <div class="lb-social-label">📣 Ready-to-post copy</div>
        <div class="lb-social-text" id="lb-social-text"></div>
      </div>
      <div class="lb-download">
        <a class="btn btn-gold" id="lb-dl" download>⬇ Download</a>
        <button class="btn btn-outline" id="lb-copy-social" style="display:none">Copy social post</button>
        <span class="copy-confirm" id="copy-confirm">Copied!</span>
      </div>
    </div>
  </div>
</div>

<script>
const ITEMS = {items_js};

let activeWeek = 0;
let activeIndex = 0;
let visibleItems = [];

function weekShort(w) {{
  return ["W1","W2","W3","W4"][w - 1];
}}

function render() {{
  const q = document.getElementById("search").value.toLowerCase().trim();
  visibleItems = ITEMS.filter(item => {{
    if (activeWeek && item.week !== activeWeek) return false;
    if (q && !item.title.toLowerCase().includes(q) && !item.caption.toLowerCase().includes(q)) return false;
    return true;
  }});

  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  document.getElementById("count").textContent = visibleItems.length + " image" + (visibleItems.length !== 1 ? "s" : "");

  if (!visibleItems.length) {{
    grid.innerHTML = '<div class="empty">No images match your search.</div>';
    return;
  }}

  visibleItems.forEach((item, i) => {{
    const isSquare = item.src.includes("05-the-attention") || item.src.includes("07-the-react") ||
                     item.src.includes("04-augmentation") || item.src.includes("07-agency");
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <img class="card-img${{isSquare ? " square" : ""}}" src="${{item.src}}" alt="${{item.title}}" loading="lazy">
      <div class="card-body">
        <div class="card-meta">
          <span class="week-badge">${{weekShort(item.week)}} · ${{item.weekLabel.replace(/Week \\d — /, "")}}</span>
          ${{item.social ? '<span class="social-badge">📣 Social</span>' : ""}}
        </div>
        <div class="card-title">${{item.title}}</div>
        <div class="card-caption">${{item.caption}}</div>
      </div>`;
    card.addEventListener("click", () => openLightbox(i));
    grid.appendChild(card);
  }});
}}

function openLightbox(i) {{
  activeIndex = i;
  const item = visibleItems[i];
  document.getElementById("lb-img").src = item.src;
  document.getElementById("lb-week").textContent = item.weekLabel;
  document.getElementById("lb-title").textContent = item.title;
  document.getElementById("lb-caption").textContent = item.caption;
  document.getElementById("lb-dl").href = item.src;
  document.getElementById("lb-dl").download = item.src.split("/").pop();

  const socialBadge = document.getElementById("lb-social-badge");
  const socialBox = document.getElementById("lb-social-box");
  const copyBtn = document.getElementById("lb-copy-social");
  const confirmEl = document.getElementById("copy-confirm");

  if (item.social) {{
    socialBadge.style.display = "";
    socialBox.style.display = "";
    document.getElementById("lb-social-text").textContent = item.social;
    copyBtn.style.display = "";
  }} else {{
    socialBadge.style.display = "none";
    socialBox.style.display = "none";
    copyBtn.style.display = "none";
  }}
  confirmEl.classList.remove("show");

  document.getElementById("lightbox").classList.add("open");
  document.body.style.overflow = "hidden";
}}

function closeLightbox() {{
  document.getElementById("lightbox").classList.remove("open");
  document.body.style.overflow = "";
}}

document.getElementById("lb-close").addEventListener("click", closeLightbox);
document.getElementById("lightbox").addEventListener("click", e => {{ if (e.target === document.getElementById("lightbox")) closeLightbox(); }});

document.getElementById("lb-prev").addEventListener("click", e => {{
  e.stopPropagation();
  openLightbox((activeIndex - 1 + visibleItems.length) % visibleItems.length);
}});
document.getElementById("lb-next").addEventListener("click", e => {{
  e.stopPropagation();
  openLightbox((activeIndex + 1) % visibleItems.length);
}});

document.getElementById("lb-copy-social").addEventListener("click", () => {{
  const item = visibleItems[activeIndex];
  if (!item.social) return;
  navigator.clipboard.writeText(item.social).then(() => {{
    const el = document.getElementById("copy-confirm");
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2000);
  }});
}});

document.addEventListener("keydown", e => {{
  if (!document.getElementById("lightbox").classList.contains("open")) return;
  if (e.key === "Escape") closeLightbox();
  if (e.key === "ArrowLeft") openLightbox((activeIndex - 1 + visibleItems.length) % visibleItems.length);
  if (e.key === "ArrowRight") openLightbox((activeIndex + 1) % visibleItems.length);
}});

document.querySelectorAll(".tab").forEach(tab => {{
  tab.addEventListener("click", () => {{
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    activeWeek = parseInt(tab.dataset.week);
    render();
  }});
}});

document.getElementById("search").addEventListener("input", render);

render();
</script>
</body>
</html>"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html = build_viewer()
    out = OUTPUT_DIR / "viewer.html"
    out.write_text(html, encoding="utf-8")
    print(f"Viewer: {out}")
    print(f"Images: {len(RAP_IMAGES)} entries across 4 weeks")


if __name__ == "__main__":
    main()
