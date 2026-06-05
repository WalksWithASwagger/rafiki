"""CSS helpers for the master library renderer."""

from __future__ import annotations


def _library_extra_css() -> str:
    return """<style>
.portal-mode-nav {
  display: flex;
  gap: 0.45rem;
  padding: 0.65rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: rgba(0,0,0,0.14);
  overflow-x: auto;
}
.portal-mode-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  border-radius: 8px;
  padding: 0.42rem 0.75rem;
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
  white-space: nowrap;
}
.portal-mode-btn:hover {
  border-color: var(--accent);
  color: var(--ink);
}
.portal-mode-btn.active {
  background: rgba(0,200,180,0.12);
  border-color: rgba(0,200,180,0.38);
  color: var(--teal);
  font-weight: 700;
}
.portal-mode-btn:focus-visible,
.filter-btn:focus-visible,
.filter-select-label select:focus-visible,
.sort-select:focus-visible,
.btn-rate:focus-visible,
.lineage-copy:focus-visible,
.run-detail-close:focus-visible,
.run-lineage-comparison button:focus-visible,
.atlas-filter-banner button:focus-visible,
.atlas-story-step button:focus-visible,
.atlas-module button:focus-visible,
.atlas-unmapped button:focus-visible,
.curriculum-context-card button:focus-visible,
.studio-style-card-actions button:focus-visible,
.workflow-actions button:focus-visible,
.studio-submit:focus-visible,
.studio-inline-btn:focus-visible,
.portal-action-submit:focus-visible,
.ops-billing-form button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 2px solid var(--teal);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0,200,180,0.16);
}
.portal-mode-panel[hidden] {
  display: none !important;
}
.mode-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin: 1rem 1.5rem 0.35rem;
}
.mode-heading h2 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}
.mode-heading p {
  margin: 0;
  color: var(--dim);
  font-size: 0.82rem;
}
.mode-note {
  border: 1px solid rgba(0,200,180,0.24);
  background: rgba(0,200,180,0.08);
  border-radius: 8px;
  color: var(--teal);
  padding: 0.35rem 0.55rem;
  font-size: 0.72rem;
  white-space: nowrap;
}
.atlas-filter-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 1.5rem 0;
  border: 1px solid rgba(0,200,180,0.28);
  background: rgba(0,200,180,0.08);
  border-radius: 8px;
  color: var(--ink);
  padding: 0.55rem 0.65rem;
  font-size: 0.78rem;
}
.atlas-filter-banner[hidden] {
  display: none !important;
}
.atlas-filter-banner button,
.atlas-story-step button,
.atlas-module button,
.atlas-unmapped button {
  border: 1px solid rgba(0,200,180,0.28);
  background: rgba(0,200,180,0.10);
  color: var(--teal);
  border-radius: 8px;
  padding: 0.4rem 0.6rem;
  font: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  white-space: nowrap;
}
.atlas-filter-banner button:hover,
.atlas-story-step button:hover,
.atlas-module button:hover,
.atlas-unmapped button:hover {
  border-color: var(--teal);
}
.atlas-story-step button:disabled,
.atlas-module button:disabled,
.atlas-unmapped button:disabled {
  cursor: default;
  opacity: 0.48;
  border-color: var(--border);
  color: var(--dim);
}
.atlas-panel {
  margin: 1rem 1.5rem 4rem;
}
.atlas-heading,
.atlas-unmapped,
.atlas-program {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(255,255,255,0.025);
}
.atlas-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
}
.atlas-heading h2,
.atlas-unmapped h3,
.atlas-program h3,
.atlas-story-step h4,
.atlas-module h4 {
  margin: 0;
}
.atlas-heading p,
.atlas-unmapped p,
.atlas-program p,
.atlas-story-step p,
.atlas-module p {
  margin: 0.25rem 0 0;
  color: var(--dim);
  font-size: 0.82rem;
}
.atlas-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(95px, 1fr));
  gap: 0.45rem;
  min-width: min(310px, 100%);
}
.atlas-summary span,
.atlas-program-count {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(0,0,0,0.12);
  padding: 0.55rem;
  color: var(--dim);
  font-size: 0.68rem;
}
.atlas-summary strong,
.atlas-program-count strong {
  color: var(--ink);
  display: block;
  font-size: 1.05rem;
}
.atlas-unmapped {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 0.85rem;
  padding: 0.8rem 1rem;
}
.atlas-concept-graph {
  display: grid;
  grid-template-columns: minmax(180px, 0.35fr) minmax(0, 1fr);
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(255,255,255,0.025);
  margin-top: 0.85rem;
  padding: 0.9rem 1rem;
  overflow: hidden;
}
.atlas-concept-graph h3 {
  margin: 0;
  font-size: 0.88rem;
}
.atlas-concept-graph p {
  margin: 0.25rem 0 0;
  color: var(--dim);
  font-size: 0.76rem;
  line-height: 1.35;
}
.atlas-concept-graph svg {
  width: 100%;
  max-height: 260px;
}
.atlas-graph-edges line {
  stroke: rgba(0,200,180,0.24);
  stroke-width: 1.2;
}
.atlas-graph-edges text {
  fill: var(--dim);
  font-size: 9px;
  text-anchor: middle;
}
.atlas-graph-nodes circle {
  fill: rgba(124,106,247,0.9);
  stroke: rgba(255,255,255,0.72);
  stroke-width: 1.5;
}
.atlas-graph-nodes text {
  fill: var(--ink);
  font-size: 10px;
  text-anchor: middle;
}
.atlas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 0.85rem;
  margin-top: 0.85rem;
}
.atlas-program {
  padding: 1rem;
}
.atlas-program-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.atlas-program-count {
  min-width: 82px;
  text-align: right;
  flex-shrink: 0;
}
.atlas-competencies {
  color: var(--teal);
  font-size: 0.72rem;
  margin-top: 0.55rem;
}
.atlas-modules {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.8rem;
}
.atlas-module,
.atlas-story-step {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.7rem;
  background: rgba(0,0,0,0.10);
}
.atlas-module span,
.atlas-story-step span {
  display: block;
  color: var(--dim);
  font-size: 0.68rem;
  margin-top: 0.3rem;
}
.atlas-evaluation-summary {
  border: 1px solid rgba(244,211,94,0.20);
  border-radius: 4px;
  color: #f4d35e;
  background: rgba(244,211,94,0.06);
  display: inline-block;
  font-size: 0.66rem;
  line-height: 1.25;
  margin-top: 0.5rem;
  padding: 0.22rem 0.38rem;
}
.atlas-teaching-block {
  border-top: 1px solid var(--border);
  margin-top: 0.65rem;
  padding-top: 0.55rem;
}
.atlas-teaching-block h5 {
  color: var(--dim);
  font-size: 0.64rem;
  letter-spacing: 0.04em;
  margin: 0 0 0.35rem;
  text-transform: uppercase;
}
.atlas-teaching-block ul {
  display: grid;
  gap: 0.32rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.atlas-teaching-block li {
  color: var(--ink);
  font-size: 0.72rem;
  line-height: 1.35;
}
.atlas-rubric-item,
.atlas-concept-link {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: rgba(255,255,255,0.025);
  padding: 0.45rem 0.5rem;
}
.atlas-rubric-item strong,
.atlas-rubric-item span,
.atlas-rubric-item em,
.atlas-concept-link strong,
.atlas-concept-link span {
  display: block;
  margin: 0;
}
.atlas-rubric-item strong,
.atlas-concept-link strong {
  color: var(--ink);
  font-size: 0.72rem;
}
.atlas-rubric-item span,
.atlas-concept-link span {
  color: var(--dim);
  font-size: 0.68rem;
}
.atlas-rubric-item em {
  color: var(--teal);
  font-size: 0.66rem;
  font-style: normal;
  margin-top: 0.25rem;
}
.atlas-concept-link {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 0.35rem;
  align-items: center;
}
.atlas-concept-link span {
  border: 1px solid rgba(0,200,180,0.24);
  border-radius: 999px;
  color: var(--teal);
  padding: 0.08rem 0.3rem;
  text-align: center;
  white-space: nowrap;
}
.atlas-empty {
  color: var(--dim);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
}
.teal-pill {
  background: rgba(0,200,180,0.12);
  border: 1px solid rgba(0,200,180,0.3);
  color: var(--teal);
}
.chip-sep {
  color: var(--border);
  margin: 0 0.1rem;
  font-size: 0.85rem;
}
.proj-badge {
  font-size: 0.62rem;
  background: rgba(0,200,180,0.1);
  border: 1px solid rgba(0,200,180,0.2);
  color: var(--teal);
  padding: 0.08rem 0.3rem;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  white-space: nowrap;
  flex-shrink: 0;
}
.card-meta-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.65rem 0;
  min-height: 1.35rem;
}
.approval-badge,
.filename-warning-badge,
.metadata-state-badge,
.feedback-badge,
.evaluation-badge,
.model-badge,
.tag {
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--dim);
  font-size: 0.58rem;
  line-height: 1.1;
  padding: 0.14rem 0.3rem;
  white-space: nowrap;
}
.filename-warning-badge:empty {
  display: none;
}
.metadata-state-badge:empty {
  display: none;
}
.feedback-badge:empty {
  display: none;
}
.evaluation-badge:empty {
  display: none;
}
.metadata-state-on {
  color: #d7c7ff;
  border-color: rgba(124,106,247,0.34);
  background: rgba(124,106,247,0.12);
  text-transform: capitalize;
}
.feedback-on {
  color: #9ee7bf;
  border-color: rgba(67,210,126,0.34);
  background: rgba(67,210,126,0.10);
  text-transform: capitalize;
}
.evaluation-on {
  color: #f4d35e;
  border-color: rgba(244,211,94,0.32);
  background: rgba(244,211,94,0.10);
  text-transform: capitalize;
}
.evaluation-revise {
  color: #ffd78f;
  border-color: rgba(255,193,94,0.34);
  background: rgba(255,193,94,0.10);
}
.evaluation-reject {
  color: #ff9da3;
  border-color: rgba(255,100,120,0.30);
  background: rgba(255,100,120,0.10);
}
.filename-warning-exact,
.filename-warning-similar {
  color: #ffd78f;
  border-color: rgba(255,193,94,0.34);
  background: rgba(255,193,94,0.10);
}
.filename-warning-similar {
  color: #d7c7ff;
  border-color: rgba(124,106,247,0.34);
  background: rgba(124,106,247,0.12);
}
.approval-approved {
  border-color: rgba(0,200,180,0.32);
  background: rgba(0,200,180,0.10);
  color: var(--teal);
}
.model-badge {
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
.card-title {
  color: var(--ink);
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.25;
  padding: 0.38rem 0.65rem 0;
}
.tag-row {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  padding: 0.35rem 0.65rem 0;
  min-height: 1rem;
}
.lineage-row {
  display: flex;
  align-items: center;
  gap: 0.28rem;
  flex-wrap: wrap;
  padding: 0.42rem 0.65rem 0;
}
.lineage-chip,
.lineage-copy {
  border: 1px solid var(--border);
  border-radius: 5px;
  background: rgba(0,0,0,0.12);
  color: var(--dim);
  font-size: 0.58rem;
  line-height: 1.1;
  padding: 0.14rem 0.32rem;
}
.lineage-next {
  color: #9ee7bf;
  border-color: rgba(67,210,126,0.28);
  background: rgba(67,210,126,0.08);
}
.lineage-copy {
  cursor: pointer;
  font: inherit;
  font-size: 0.58rem;
}
.lineage-copy:hover {
  color: var(--teal);
  border-color: rgba(0,200,180,0.34);
}
#search {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--ink);
  padding: 0.22rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-family: inherit;
  outline: none;
  flex: 1;
  min-width: 100px;
  max-width: 220px;
  transition: border-color 0.15s;
}
#search:focus, #search:hover { border-color: var(--accent); }
#search::placeholder { color: var(--dim); opacity: 0.6; }
.filter-select-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--dim);
  font-size: 0.72rem;
  user-select: none;
}
.filter-select-label select {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: inherit;
  outline: none;
  max-width: 170px;
}
.filter-select-label select:focus,
.filter-select-label select:hover {
  border-color: var(--accent);
  color: var(--ink);
}
.keyboard-hint {
  color: var(--dim);
  font-size: 0.68rem;
  white-space: nowrap;
  opacity: 0.78;
}
.sort-select {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--dim);
  padding: 0.22rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
  font-family: inherit;
  outline: none;
}
.sort-select:focus, .sort-select:hover { border-color: var(--accent); color: var(--ink); }
.card.active-card {
  border-color: var(--teal);
  box-shadow: 0 0 0 2px rgba(0,200,180,0.22), 0 8px 32px rgba(0,200,180,0.12);
}
.btn-rate.detail {
  color: var(--teal);
  border-color: rgba(0,200,180,0.24);
}
.run-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(480px, 92vw);
  background: #12101f;
  border-left: 1px solid var(--border);
  box-shadow: -18px 0 48px rgba(0,0,0,0.35);
  transform: translateX(105%);
  transition: transform 0.18s ease;
  z-index: 8500;
  display: flex;
  flex-direction: column;
}
.run-detail-panel.open {
  transform: translateX(0);
}
.run-detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}
.run-detail-head h2 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}
.run-detail-head p {
  margin: 0;
  color: var(--dim);
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}
.run-detail-close {
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  flex-shrink: 0;
}
.run-detail-body {
  padding: 1rem;
  overflow: auto;
}
.run-detail-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.run-detail-links a {
  color: var(--teal);
  border: 1px solid rgba(0,200,180,0.22);
  background: rgba(0,200,180,0.08);
  border-radius: 8px;
  padding: 0.32rem 0.55rem;
  text-decoration: none;
  font-size: 0.75rem;
}
.run-detail-links a:hover {
  border-color: var(--teal);
}
.run-detail-warning {
  display: none;
  border: 1px solid rgba(255,193,94,0.26);
  background: rgba(255,193,94,0.08);
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  color: var(--ink);
}
.run-detail-warning-exact,
.run-detail-warning-similar {
  display: block;
}
.run-detail-warning-similar {
  border-color: rgba(124,106,247,0.28);
  background: rgba(124,106,247,0.10);
}
.run-detail-warning-title {
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.run-detail-warning p {
  margin: 0;
  color: var(--dim);
  font-size: 0.74rem;
  line-height: 1.45;
}
.run-detail-warning-list {
  margin: 0.55rem 0 0;
  padding-left: 1rem;
  color: var(--dim);
  font-size: 0.7rem;
}
.run-detail-warning-list li {
  margin: 0.25rem 0;
  overflow-wrap: anywhere;
}
.run-detail-warning-list span {
  margin-left: 0.35rem;
}
.run-detail-fields {
  display: grid;
  grid-template-columns: minmax(6rem, 0.38fr) 1fr;
  gap: 0.35rem 0.75rem;
  margin: 0 0 1rem;
  font-size: 0.76rem;
}
.run-detail-fields dt {
  color: var(--dim);
}
.run-detail-fields dd {
  color: var(--ink);
  overflow-wrap: anywhere;
}
.run-decision-summary {
  border: 1px solid rgba(244,211,94,0.22);
  background: rgba(244,211,94,0.06);
  border-radius: 8px;
  padding: 0.75rem;
  margin: 0 0 1rem;
}
.run-lineage-comparison {
  border: 1px solid rgba(124,106,247,0.24);
  background: rgba(124,106,247,0.075);
  border-radius: 8px;
  padding: 0.75rem;
  margin: 0 0 1rem;
}
.lineage-comparison-missing {
  border-color: rgba(255,193,94,0.24);
  background: rgba(255,193,94,0.07);
}
.lineage-comparison-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}
.run-lineage-comparison h3,
.run-decision-summary h3 {
  margin: 0 0 0.55rem;
  font-size: 0.82rem;
}
.lineage-comparison-head h3 {
  margin-bottom: 0.2rem;
}
.run-lineage-comparison p,
.run-lineage-comparison small,
.lineage-empty {
  color: var(--dim);
  font-size: 0.72rem;
  line-height: 1.45;
  margin: 0;
}
.run-lineage-comparison code {
  display: block;
  color: var(--teal);
  font-size: 0.68rem;
  margin-top: 0.45rem;
  overflow-wrap: anywhere;
}
.lineage-comparison-head span {
  align-self: flex-start;
  border: 1px solid rgba(124,106,247,0.28);
  border-radius: 999px;
  color: #d7c7ff;
  background: rgba(124,106,247,0.12);
  font-size: 0.66rem;
  padding: 0.22rem 0.45rem;
  white-space: nowrap;
}
.run-lineage-comparison table {
  border-collapse: collapse;
  margin-top: 0.55rem;
  width: 100%;
}
.run-lineage-comparison th,
.run-lineage-comparison td {
  border-top: 1px solid rgba(255,255,255,0.075);
  color: var(--dim);
  font-size: 0.68rem;
  line-height: 1.35;
  max-width: 13rem;
  overflow-wrap: anywhere;
  padding: 0.38rem 0.25rem;
  text-align: left;
  vertical-align: top;
}
.run-lineage-comparison thead th {
  color: var(--ink);
  font-size: 0.62rem;
  text-transform: uppercase;
}
.run-lineage-comparison tbody th {
  color: var(--ink);
}
.lineage-changed td {
  color: #d7c7ff;
}
.run-lineage-comparison button {
  border: 1px solid rgba(0,200,180,0.24);
  background: rgba(0,200,180,0.08);
  color: var(--teal);
  border-radius: 6px;
  cursor: pointer;
  margin-top: 0.65rem;
  padding: 0.35rem 0.55rem;
  font-size: 0.72rem;
}
.run-lineage-comparison button:hover {
  border-color: var(--teal);
}
.run-decision-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.run-decision-chip {
  border: 1px solid rgba(244,211,94,0.24);
  border-radius: 4px;
  color: var(--dim);
  background: rgba(0,0,0,0.16);
  font-size: 0.66rem;
  line-height: 1.1;
  padding: 0.2rem 0.38rem;
}
.run-decision-score {
  color: #f4d35e;
}
.run-detail-curriculum,
.run-detail-metadata,
.run-detail-feedback,
.run-detail-evaluation {
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.025);
  border-radius: 8px;
  padding: 0.8rem;
  margin: 0 0 1rem;
}
.run-detail-curriculum {
  border-color: rgba(0,200,180,0.20);
  background: rgba(0,200,180,0.045);
}
.run-detail-curriculum h3,
.run-detail-metadata h3,
.run-detail-feedback h3,
.run-detail-evaluation h3 {
  margin: 0 0 0.65rem;
  font-size: 0.85rem;
}
.curriculum-context-card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  padding: 0.65rem;
  margin-top: 0.6rem;
  background: rgba(0,0,0,0.16);
}
.curriculum-context-card h4 {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
}
.curriculum-context-card p,
.curriculum-context-empty,
.curriculum-context-why {
  margin: 0 0 0.5rem;
  color: var(--dim);
  font-size: 0.72rem;
  line-height: 1.45;
}
.curriculum-context-list {
  margin-top: 0.55rem;
}
.curriculum-context-list strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--ink);
  font-size: 0.7rem;
}
.curriculum-context-list ul {
  margin: 0;
  padding-left: 1rem;
  color: var(--dim);
  font-size: 0.7rem;
  line-height: 1.45;
}
.curriculum-context-card button {
  border: 1px solid rgba(0,200,180,0.24);
  background: rgba(0,200,180,0.08);
  color: var(--teal);
  border-radius: 6px;
  cursor: pointer;
  margin-top: 0.6rem;
  padding: 0.35rem 0.55rem;
  font-size: 0.72rem;
}
.curriculum-context-card button:hover {
  border-color: var(--teal);
}
.run-detail-metadata label,
.run-detail-feedback label,
.run-detail-evaluation label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-bottom: 0.65rem;
}
.run-detail-metadata label span,
.run-detail-feedback label span,
.run-detail-evaluation label span {
  color: var(--dim);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.run-detail-metadata input[type="text"],
.run-detail-metadata select,
.run-detail-evaluation input[type="text"],
.run-detail-feedback select,
.run-detail-evaluation select,
.run-detail-feedback textarea,
.run-detail-evaluation textarea {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  background: rgba(255,255,255,0.035);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 8px;
  padding: 0.55rem 0.65rem;
  font: inherit;
  font-size: 0.76rem;
}
.run-detail-feedback textarea {
  resize: vertical;
}
.run-detail-evaluation textarea {
  resize: vertical;
}
.metadata-state-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.35rem 0.65rem;
  margin-bottom: 0.65rem;
  color: var(--dim);
  font-size: 0.74rem;
}
.metadata-state-grid label {
  flex-direction: row;
  align-items: center;
  margin: 0;
}
.metadata-actions,
.feedback-actions,
.evaluation-actions {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}
.metadata-actions button,
.feedback-actions button,
.evaluation-actions button {
  border: 1px solid rgba(0,200,180,0.24);
  background: rgba(0,200,180,0.09);
  color: var(--teal);
  border-radius: 8px;
  padding: 0.42rem 0.62rem;
  font: inherit;
  font-size: 0.73rem;
  cursor: pointer;
}
.metadata-actions button:hover,
.feedback-actions button:hover,
.evaluation-actions button:hover {
  border-color: var(--teal);
}
.metadata-status,
.feedback-status,
.evaluation-status {
  min-height: 1rem;
  margin-top: 0.55rem;
  color: var(--dim);
  font-size: 0.72rem;
}
.metadata-status-error,
.feedback-status-error,
.evaluation-status-error { color: #ff8f8f; }
.metadata-status-busy,
.feedback-status-busy,
.evaluation-status-busy { color: var(--teal); }
.metadata-status-success,
.feedback-status-success,
.evaluation-status-success { color: #9ee7bf; }
.run-detail-json {
  border: 1px solid var(--border);
  background: rgba(0,0,0,0.22);
  border-radius: 8px;
  padding: 0.75rem;
  color: var(--dim);
  font-size: 0.68rem;
  line-height: 1.45;
  overflow: auto;
  max-height: 42vh;
}
.studio-panel {
  margin: 1rem 1.5rem 0.9rem;
  padding: 1rem 1rem 0.9rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background:
    linear-gradient(145deg, rgba(124,106,247,0.10), rgba(0,200,180,0.05)),
    var(--surface);
}
.studio-heading {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.9rem;
}
.studio-heading h2 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}
.studio-heading p {
  margin: 0;
  color: var(--dim);
  font-size: 0.83rem;
  max-width: 62ch;
}
.studio-note {
  color: var(--teal);
  font-size: 0.72rem;
  border: 1px solid rgba(0,200,180,0.22);
  background: rgba(0,200,180,0.08);
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}
.studio-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.studio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
}
.studio-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.studio-wide { grid-column: 1 / -1; }
.studio-field span {
  color: var(--dim);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.studio-field input,
.studio-field select,
.studio-field textarea {
  width: 100%;
  min-width: 0;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  font: inherit;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
  box-sizing: border-box;
}
.studio-field textarea {
  resize: vertical;
  min-height: 7rem;
}
.studio-field input:focus,
.studio-field select:focus,
.studio-field textarea:focus,
.studio-field input:hover,
.studio-field select:hover,
.studio-field textarea:hover {
  border-color: var(--accent);
  background: rgba(255,255,255,0.05);
}
.workflow-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.workflow-heading {
  margin-bottom: 0;
}
.workflow-chain {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.5rem;
}
.workflow-chain span {
  border: 1px solid rgba(0,200,180,0.20);
  border-radius: 8px;
  background: rgba(0,200,180,0.07);
  color: var(--teal);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.55rem 0.6rem;
  text-align: center;
}
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.85rem;
}
.workflow-card {
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 8px;
  background: rgba(0,0,0,0.16);
  padding: 0.95rem;
}
.workflow-card-muted {
  background: rgba(255,255,255,0.03);
}
.workflow-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}
.workflow-card h3 {
  margin: 0;
  font-size: 0.95rem;
}
.workflow-card code {
  color: var(--teal);
  font-size: 0.7rem;
  white-space: normal;
  overflow-wrap: anywhere;
}
.workflow-card p {
  color: var(--dim);
  font-size: 0.78rem;
  line-height: 1.45;
  margin: 0 0 0.8rem;
}
.workflow-card dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
  margin: 0 0 0.85rem;
}
.workflow-card dl div {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.55rem;
}
.workflow-card dt {
  color: var(--dim);
  font-size: 0.62rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
  text-transform: uppercase;
}
.workflow-card dd {
  color: var(--ink);
  font-size: 0.78rem;
  margin: 0;
}
.workflow-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}
.workflow-actions button {
  border: 1px solid rgba(0,200,180,0.28);
  border-radius: 8px;
  background: rgba(0,200,180,0.10);
  color: var(--teal);
  cursor: pointer;
  font: inherit;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 0.5rem 0.72rem;
}
.workflow-actions button:hover {
  border-color: var(--teal);
  background: rgba(0,200,180,0.16);
}
.studio-style-guidance {
  color: var(--dim);
  font-size: 0.72rem;
  line-height: 1.35;
}
.studio-style-guidance-error {
  color: #ffb4a8;
}
.studio-style-reference {
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 10px;
  background: rgba(0,0,0,0.16);
  padding: 0.8rem;
}
.studio-style-reference-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.studio-style-reference-head h3 {
  margin: 0 0 0.2rem;
  font-size: 0.9rem;
}
.studio-style-reference-head p {
  margin: 0;
  color: var(--dim);
  font-size: 0.76rem;
  line-height: 1.4;
}
.studio-style-search {
  width: min(320px, 100%);
  flex-shrink: 0;
}
.studio-style-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.7rem;
}
.studio-style-card,
.studio-style-empty {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  padding: 0.72rem;
}
.studio-style-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 220px;
}
.studio-style-card.is-active {
  border-color: rgba(0,200,180,0.62);
  background: rgba(0,200,180,0.08);
}
.studio-style-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.studio-style-card-top code {
  color: var(--teal);
  font-size: 0.76rem;
}
.studio-style-badge {
  border: 1px solid rgba(0,200,180,0.28);
  border-radius: 999px;
  color: var(--teal);
  background: rgba(0,200,180,0.08);
  padding: 0.12rem 0.42rem;
  font-size: 0.66rem;
  white-space: nowrap;
}
.studio-style-name {
  color: var(--ink);
  font-size: 0.9rem;
  line-height: 1.25;
}
.studio-style-description,
.studio-style-context,
.studio-style-empty {
  margin: 0;
  color: var(--dim);
  font-size: 0.74rem;
  line-height: 1.42;
}
.studio-style-context {
  flex: 1;
}
.studio-style-context span {
  display: block;
  color: var(--ink);
  font-size: 0.68rem;
  font-weight: 700;
  margin-bottom: 0.16rem;
  text-transform: uppercase;
}
.studio-style-card-actions {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}
.studio-style-card-actions button {
  border: 1px solid rgba(0,200,180,0.28);
  border-radius: 8px;
  background: rgba(0,200,180,0.10);
  color: var(--teal);
  cursor: pointer;
  font: inherit;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.38rem 0.58rem;
}
.studio-style-card-actions button:hover {
  border-color: var(--teal);
  background: rgba(0,200,180,0.16);
}
.studio-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  flex-wrap: wrap;
}
.studio-check {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--dim);
  font-size: 0.8rem;
}
.studio-submit,
.studio-inline-btn {
  border: 1px solid rgba(0,200,180,0.28);
  background: rgba(0,200,180,0.13);
  color: var(--teal);
  border-radius: 10px;
  padding: 0.62rem 0.95rem;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.12s, border-color 0.12s, background 0.12s;
}
.studio-submit:hover,
.studio-inline-btn:hover {
  border-color: var(--teal);
  background: rgba(0,200,180,0.18);
  transform: translateY(-1px);
}
.studio-submit:disabled,
.studio-inline-btn:disabled {
  cursor: wait;
  opacity: 0.7;
  transform: none;
}
.studio-inline-btn {
  padding: 0.42rem 0.65rem;
}
.studio-status {
  min-height: 1.2rem;
  font-size: 0.82rem;
  color: var(--dim);
}
.studio-status-success { color: var(--ink); }
.studio-status-error { color: #ff8f8f; }
.studio-status-busy { color: var(--teal); }
.studio-status-info { color: var(--dim); }
.studio-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 0.55rem;
}
.studio-links a {
  color: var(--accent);
  text-decoration: none;
}
.studio-links a:hover { text-decoration: underline; }
.studio-hidden { display: none; }
.studio-disabled {
  opacity: 0.72;
  filter: grayscale(0.12);
}
.portal-actions-panel {
  margin: 0.8rem 1.5rem 0.9rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
}
.portal-actions-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.portal-actions-heading h2 {
  margin: 0;
  font-size: 1rem;
}
.portal-actions-note {
  color: var(--dim);
  font-size: 0.76rem;
}
.portal-actions-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem;
  align-items: end;
}
.portal-actions-form label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}
.portal-actions-form label span {
  color: var(--dim);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.portal-actions-form input[type="text"],
.portal-actions-form select {
  width: 100%;
  min-width: 0;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: var(--ink);
  border-radius: 10px;
  padding: 0.58rem 0.68rem;
  font: inherit;
  box-sizing: border-box;
}
.portal-action-toggles {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
  color: var(--dim);
  font-size: 0.78rem;
}
.portal-action-toggles label {
  flex-direction: row;
  align-items: center;
  gap: 0.35rem;
}
.portal-action-submit {
  border: 1px solid rgba(124,106,247,0.34);
  background: rgba(124,106,247,0.14);
  color: var(--accent);
  border-radius: 10px;
  padding: 0.62rem 0.95rem;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.portal-action-submit:disabled {
  cursor: wait;
  opacity: 0.7;
}
.portal-action-status {
  min-height: 1.2rem;
  margin-top: 0.75rem;
  color: var(--dim);
  font-size: 0.82rem;
}
.portal-action-status-error { color: #ff8f8f; }
.portal-action-status-busy { color: var(--teal); }
.portal-action-status-success { color: var(--ink); }
.portal-action-hidden { display: none !important; }
.ops-panel {
  margin: 0.8rem 1.5rem 0.9rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: rgba(255,255,255,0.025);
}
.ops-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.ops-heading h2 {
  margin: 0;
  font-size: 1rem;
}
.ops-note {
  color: var(--dim);
  font-size: 0.74rem;
  text-align: right;
}
.ops-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
  gap: 0.7rem;
}
.ops-tile {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(0,0,0,0.12);
  padding: 0.75rem;
  min-width: 0;
}
.ops-tile span,
.ops-tile small {
  display: block;
  color: var(--dim);
  font-size: 0.68rem;
}
.ops-tile strong {
  display: block;
  color: var(--ink);
  font-size: 1.25rem;
  line-height: 1.2;
  margin: 0.2rem 0;
}
.ops-columns,
.ops-readiness {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.85rem;
  margin-top: 0.9rem;
}
.ops-columns h3,
.ops-readiness h3,
.ops-billing-form h3 {
  margin: 0 0 0.45rem;
  color: var(--dim);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.ops-billing-form {
  display: grid;
  grid-template-columns: 1fr repeat(3, minmax(110px, 0.6fr)) auto auto;
  gap: 0.55rem;
  align-items: end;
  margin-top: 0.9rem;
}
.ops-billing-form label,
.ops-billing-form label span {
  display: block;
}
.ops-billing-form label span {
  color: var(--dim);
  font-size: 0.65rem;
  margin-bottom: 0.22rem;
}
.ops-billing-form input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: rgba(0,0,0,0.18);
  color: var(--ink);
  padding: 0.48rem 0.55rem;
}
.ops-billing-form button {
  border: 1px solid rgba(0,200,180,0.35);
  border-radius: 8px;
  background: rgba(0,200,180,0.12);
  color: var(--teal);
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}
.ops-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.ops-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.45rem 0.55rem;
  color: var(--ink);
  font-size: 0.76rem;
}
.ops-row span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ops-row small {
  display: block;
  color: var(--dim);
  overflow: hidden;
  text-overflow: ellipsis;
}
.readiness-ready strong {
  color: #9ee7bf;
}
.readiness-missing strong {
  color: #ffb4a8;
}
.readiness-optional strong {
  color: #ffd78f;
}
.ops-empty {
  color: var(--dim);
  font-size: 0.76rem;
}
@media (max-width: 820px) {
  .portal-mode-nav {
    padding: 0.55rem 1rem;
  }
  .mode-heading,
  .studio-heading {
    flex-direction: column;
  }
  .studio-style-reference-head {
    flex-direction: column;
  }
  .studio-style-search {
    width: 100%;
  }
  .studio-style-cards {
    grid-template-columns: 1fr;
  }
  .workflow-chain,
  .workflow-card dl {
    grid-template-columns: 1fr;
  }
  .workflow-card-head {
    flex-direction: column;
  }
  .mode-heading,
  .atlas-panel {
    margin-left: 1rem;
    margin-right: 1rem;
  }
  .atlas-heading,
  .atlas-unmapped,
  .atlas-concept-graph,
  .atlas-program-head,
  .portal-actions-heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .atlas-concept-graph {
    grid-template-columns: 1fr;
  }
  .atlas-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }
  .atlas-module,
  .atlas-story-step {
    flex-direction: column;
  }
  .atlas-concept-link {
    grid-template-columns: 1fr;
  }
  .ops-heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .ops-note {
    text-align: left;
  }
  .ops-billing-form {
    grid-template-columns: 1fr;
  }
  .studio-note {
    white-space: normal;
  }
}
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
  .studio-submit:hover,
  .studio-inline-btn:hover {
    transform: none;
  }
}
</style>"""
