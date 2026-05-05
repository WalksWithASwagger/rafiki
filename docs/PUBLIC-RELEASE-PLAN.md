# Public Release Plan

This document tracks the work required to make Rafiki safe, understandable,
and useful as a public open-source release.

## Goals

- Keep Rafiki local-first.
- Remove private machine assumptions from tracked files.
- Make installation and packaging predictable.
- Improve first-run onboarding for new contributors and users.
- Preserve advanced workflows without making them the default story.

## Current Release Direction

Rafiki v1 is a local tool:

- CLI for image generation and HTML-to-image rendering
- Local review portal for comparing runs and curating outputs
- Optional export and MCP integrations for advanced workflows

It is not a hosted multi-user service.

## Phase 1: Release Hygiene

- Scrub tracked local paths and project-specific machine config
- Move external project registry usage to a local override file
- Tighten `.gitignore` for local-only files and generated package artifacts
- Add an explicit npm publish allowlist so only runtime files ship
- Add CI for tests plus package smoke-checking
- Add contributor and security docs

## Phase 2: Public Product Positioning

- Rewrite the README around generic workflows instead of a single private
  ecosystem
- Document scope clearly: local-first, no hosted backend, keys stay on the
  operator's machine
- Keep project-specific prompt libraries as examples, not as the primary entry
  point
- Prefer clone-and-run onboarding until the npm distribution story is fully
  frictionless

## Phase 3: Onboarding and Interface Improvements

- Add setup diagnostics (`rafiki --doctor`)
- Improve registry and portal docs for cross-project usage
- Continue reducing repo-specific assumptions in examples and prompts
- Expand the portal as the default interface for non-terminal users

## Phase 4: High-Value Product Additions

- Prompt studio in the local portal
- Approval-first curation workflow
- Prompt/version diffing between runs
- Cost and throughput reporting by run/provider/model
- Self-contained share pages for review handoff
- Export bundles for social, Notion, and Canva

## Release Checklist

- No tracked secrets
- No tracked local absolute paths
- `python3 -m pytest -q` passes
- `npm pack --dry-run` publishes only the intended runtime surface
- README covers install, quickstart, security, scope, and common workflows
- CI runs on pull requests
