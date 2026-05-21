"""Curriculum Atlas HTML helpers for the Rafiki library portal."""

from __future__ import annotations

import json
import math
from html import escape


def _atlas_list_html(title: str, items: list[str], class_name: str) -> str:
    if not items:
        return ""
    rows = "".join(f"<li>{escape(str(item))}</li>" for item in items)
    return f"""
    <div class="atlas-teaching-block {class_name}">
      <h5>{escape(title)}</h5>
      <ul>{rows}</ul>
    </div>
    """


def _atlas_rubric_html(criteria: list[dict]) -> str:
    if not criteria:
        return ""
    rows = []
    for item in criteria:
        rows.append(
            """
            <li class="atlas-rubric-item">
              <strong>{label}</strong>
              <span>{prompt}</span>
              {scale}
            </li>
            """.format(
                label=escape(str(item.get("label") or "Criterion")),
                prompt=escape(str(item.get("prompt") or "")),
                scale=(
                    f'<em>{escape(str(item.get("scale")))}</em>'
                    if item.get("scale") else ""
                ),
            )
        )
    return """
    <div class="atlas-teaching-block atlas-rubric">
      <h5>Critique Rubric</h5>
      <ul>{rows}</ul>
    </div>
    """.format(rows="".join(rows))


def _atlas_concept_links_html(links: list[dict]) -> str:
    if not links:
        return ""
    rows = []
    for link in links:
        rows.append(
            """
            <li class="atlas-concept-link">
              <strong>{concept}</strong>
              <span>{relation}</span>
              <strong>{target}</strong>
            </li>
            """.format(
                concept=escape(str(link.get("concept") or "")),
                relation=escape(str(link.get("relation") or "related")),
                target=escape(str(link.get("target") or "")),
            )
        )
    return """
    <div class="atlas-teaching-block atlas-concepts">
      <h5>Concept Links</h5>
      <ul>{rows}</ul>
    </div>
    """.format(rows="".join(rows))


def _atlas_teaching_html(module: dict) -> str:
    blocks = [
        _atlas_list_html("Facilitator Notes", module.get("facilitator_notes") or [], "atlas-facilitator-notes"),
        _atlas_list_html("Discussion Prompts", module.get("discussion_prompts") or [], "atlas-discussion-prompts"),
        _atlas_rubric_html(module.get("critique_criteria") or []),
        _atlas_concept_links_html(module.get("concept_links") or []),
    ]
    return "".join(blocks)


def _atlas_concept_graph_html(atlas: dict) -> str:
    links = []
    for program in atlas.get("programs", []):
        for module in program.get("modules", []):
            for link in module.get("concept_links") or []:
                concept = str(link.get("concept") or "").strip()
                target = str(link.get("target") or "").strip()
                relation = str(link.get("relation") or "related").strip()
                if concept and target:
                    links.append({"concept": concept, "target": target, "relation": relation})

    if not links:
        return """
        <section class="atlas-concept-graph" aria-label="Concept graph">
          <div>
            <h3>Concept Graph</h3>
            <p>No concept links configured yet.</p>
          </div>
        </section>
        """

    node_names = []
    for link in links:
        for name in (link["concept"], link["target"]):
            if name not in node_names:
                node_names.append(name)
    node_names = node_names[:12]
    node_index = {name: idx for idx, name in enumerate(node_names)}
    graph_links = [link for link in links if link["concept"] in node_index and link["target"] in node_index][:16]

    width = 760
    height = 250
    cx = width / 2
    cy = height / 2
    radius_x = 300
    radius_y = 82
    positions = {}
    for idx, name in enumerate(node_names):
        angle = (idx / max(len(node_names), 1)) * 6.283185307179586
        positions[name] = (
            round(cx + radius_x * math.cos(angle), 2),
            round(cy + radius_y * math.sin(angle), 2),
        )

    edge_rows = []
    for link in graph_links:
        x1, y1 = positions[link["concept"]]
        x2, y2 = positions[link["target"]]
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        edge_rows.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"></line>'
            f'<text x="{mx:.2f}" y="{my:.2f}">{escape(link["relation"])}</text>'
        )

    node_rows = []
    for name in node_names:
        x, y = positions[name]
        node_rows.append(
            f'<g><circle cx="{x}" cy="{y}" r="8"></circle>'
            f'<text x="{x}" y="{y + 24}">{escape(name)}</text></g>'
        )

    return """
    <section class="atlas-concept-graph" aria-label="Concept graph">
      <div>
        <h3>Concept Graph</h3>
        <p>A compact map of the concept relationships already encoded in the Atlas.</p>
      </div>
      <svg viewBox="0 0 {width} {height}" role="img" aria-label="Curriculum concept relationships">
        <g class="atlas-graph-edges">{edges}</g>
        <g class="atlas-graph-nodes">{nodes}</g>
      </svg>
    </section>
    """.format(width=width, height=height, edges="".join(edge_rows), nodes="".join(node_rows))


def _atlas_panel_html(atlas: dict) -> str:
    summary = atlas.get("summary", {})
    programs = atlas.get("programs", [])
    program_cards = []
    for program in programs:
        modules = []
        for module in program.get("modules", []):
            program_id = json.dumps(program.get("id") or "")
            module_id = json.dumps(module.get("id") or "")
            program_id_attr = escape(str(program.get("id") or ""))
            module_id_attr = escape(str(module.get("id") or ""))
            competencies = ", ".join(module.get("competencies") or [])
            asset_count = int(module.get("asset_count") or 0)
            evaluation = module.get("evaluation_summary") if isinstance(module.get("evaluation_summary"), dict) else {}
            evaluated = int(evaluation.get("evaluated_count") or 0)
            average = evaluation.get("average_score")
            evaluation_text = f"{evaluated}/{asset_count} evaluated"
            if average:
                evaluation_text += f" · avg {average}"
            modules.append(
                """
                <div class="atlas-module" data-program-id="{program_id_attr}" data-module-id="{module_id_attr}">
                  <div>
                    <h4>{title}</h4>
                    <p>{objective}</p>
                    <span>{level}{competencies}</span>
                    <div class="atlas-evaluation-summary" data-program-id="{program_id_attr}" data-module-id="{module_id_attr}">{evaluation_text}</div>
                    {teaching}
                  </div>
                  <button type="button" onclick='focusAtlasModule({program_id}, {module_id})'{disabled}>{asset_count} asset{asset_plural}</button>
                </div>
                """.format(
                    program_id_attr=program_id_attr,
                    module_id_attr=module_id_attr,
                    title=escape(str(module.get("title") or "Untitled module")),
                    objective=escape(str(module.get("objective") or "")),
                    level=escape(str(module.get("level") or "module")),
                    competencies=escape(f" · {competencies}" if competencies else ""),
                    evaluation_text=escape(evaluation_text),
                    teaching=_atlas_teaching_html(module),
                    program_id=program_id,
                    module_id=module_id,
                    disabled=" disabled" if asset_count == 0 else "",
                    asset_count=asset_count,
                    asset_plural="" if asset_count == 1 else "s",
                )
            )
        competencies = ", ".join(program.get("competencies") or [])
        program_cards.append(
            """
            <article class="atlas-program" data-program="{program_id}">
              <div class="atlas-program-head">
                <div>
                  <h3>{title}</h3>
                  <p>{summary}</p>
                </div>
                <div class="atlas-program-count">
                  <strong>{asset_count}</strong>
                  <span>linked asset{asset_plural}</span>
                </div>
              </div>
              <div class="atlas-competencies">{competencies}</div>
              <div class="atlas-modules">{modules}</div>
            </article>
            """.format(
                program_id=escape(str(program.get("id") or "")),
                title=escape(str(program.get("title") or "Untitled program")),
                summary=escape(str(program.get("summary") or "")),
                asset_count=int(program.get("asset_count") or 0),
                asset_plural="" if int(program.get("asset_count") or 0) == 1 else "s",
                competencies=escape(competencies),
                modules="".join(modules),
            )
        )

    unmapped_assets = int(summary.get("unmapped_assets") or 0)
    return """
<section class="atlas-panel" id="curriculum-atlas-panel">
  <div class="atlas-heading">
    <div>
      <h2>Curriculum Atlas</h2>
      <p>Programs, modules, competencies, and archive links from <code>config/curriculum-atlas.json</code>.</p>
    </div>
    <div class="atlas-summary">
      <span><strong>{program_count}</strong> programs</span>
      <span><strong>{module_count}</strong> modules</span>
      <span><strong>{linked_assets}</strong> linked assets</span>
      <span><strong>{unmapped_assets}</strong> unmapped</span>
    </div>
  </div>
  {concept_graph}
  <div class="atlas-unmapped">
    <div>
      <h3>Mapping Queue</h3>
      <p>Archive cards that do not match the current curriculum scaffold yet.</p>
    </div>
    <button type="button" onclick="focusAtlasUnmapped()"{unmapped_disabled}>{unmapped_assets} unmapped asset{unmapped_plural}</button>
  </div>
  <div class="atlas-grid">
    {program_cards}
  </div>
</section>
""".format(
        program_count=int(summary.get("programs") or 0),
        module_count=int(summary.get("modules") or 0),
        linked_assets=int(summary.get("linked_assets") or 0),
        unmapped_assets=unmapped_assets,
        unmapped_disabled=" disabled" if unmapped_assets == 0 else "",
        unmapped_plural="" if unmapped_assets == 1 else "s",
        concept_graph=_atlas_concept_graph_html(atlas),
        program_cards="".join(program_cards) or '<div class="atlas-empty">No curriculum programs configured yet.</div>',
    )
