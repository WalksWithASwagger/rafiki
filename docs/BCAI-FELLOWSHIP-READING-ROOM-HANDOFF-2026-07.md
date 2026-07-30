# BC + AI Builders Fellowship Reading Room Handoff

Date: 2026-07-30

## Summary

The AI Builders Fellowship launch package uses the approved Reading Room
direction: charcoal, bone, graphite, sparse acid-lime, Canadian
government-publication modernism, catalogue grids, survey contours, and tactile
halftone grain.

The local package contains:

- five approved launch assets;
- a four-candidate GPT Image 2 versus Gemini bake-off;
- a six-call second variation round with three selected candidates;
- provider receipts, exact prompts, source ledgers, brand-reference ledgers,
  QA reports, and review viewers.

The earlier amber, aurora, bioluminescent, and forest treatments remain
preserved as rejected or legacy work. Nothing was deleted or silently rerolled.

## Public Boundary

Rafiki intentionally keeps campaign prompts, source media, provider receipts,
and generated output under gitignored `prompts/`, `assets/`, and `output/`
trees. This tracked handoff records the package without publishing private
working material or generated images into the public repository.

No image, prompt, reference, provider receipt, website integration, deployment,
or public release is part of this commit.

## Local Package Map

| Purpose | Repo-relative path |
| --- | --- |
| Approved style and provenance sources | `assets/bcai-fellowship-2026-07/` |
| Prompt packet and verification tools | `prompts/bcai-fellowship-2026-07/` |
| Full run archive | `output/bcai-fellowship-2026-07/` |
| Approved five-asset viewer | `output/bcai-fellowship-2026-07/approved/viewer.html` |
| Final launch-set run | `output/bcai-fellowship-2026-07/run-final-launch-set/` |
| Second variation run | `output/bcai-fellowship-2026-07/run-reading-room-variations-r2/` |

At closeout, the three local trees contain 236 files and occupy approximately
202 MB. Generated viewers and registry pages are rebuildable; the image files,
manifests, ledgers, and receipts are the preservation-critical records.

## Approved Launch Set

| File | Dimensions | SHA-256 |
| --- | ---: | --- |
| `01-fellowship-master-16x9.png` | 2048x1152 | `8e851635b8e54b58179f9224544300ace72ec71ac99d0b191b208f380d349be0` |
| `02-fellowship-keynote-16x9.png` | 2048x1152 | `af66be501d1db52865ccbd4e326c7dce86d5788e15a19d45744896c88d29f7f5` |
| `03-fellowship-og-linkedin.png` | 2048x1072 | `26caff178197c5f0e729a3ba700f486239d3aa3bca2a4f5563efc46dbb38ebdc` |
| `04-fellowship-launch-square.png` | 2048x2048 | `305f91a01b7f2d6e92fc381f8188a8e5d2e4e8754aa298117274e183a4240c61` |
| `05-fellowship-story-9x16.png` | 1152x2048 | `a0633ff8eba6dc714f8cd54b85cb96cbf68743a6e2b23a97005509a7e0387ccf` |

The approved directory contains exactly these five assets. The source final
run uses `gpt-image-2`; all five passed native-dimension, locked-copy, OCR,
palette, motif, and visual-review gates.

## Selected Second-Round Variations

| File | Dimensions | Score | Notes | SHA-256 |
| --- | ---: | ---: | --- | --- |
| `01-survey-grant-ledger-wide.png` | 2048x1152 | 96/100 | Wide survey-ledger treatment with the approved `$5,000` campaign copy. | `6f588b5cb9ca947aeaca6fe53256fea98b02abdb7b492191bf274b04253b49fc` |
| `03b-reading-room-grant-card-square-logos-repair.png` | 2048x2048 | 95/100 | Includes faithful Internet Archive Canada and BC + AI Ecosystem marks exactly once, plus `$5,000 · SIX WEEKS`. | `7b4511004014a348c1753ef6884aad713781c12eded6946607d8d27d692625a4` |
| `04-vertical-grant-register-story.png` | 1152x2048 | 95/100 | Vertical grant-register treatment with exact campaign copy and URL. | `7d2f972042c7b7cdc6d1164a8c253062e322a6621c2b7cc21e0bf9e50d909159` |

All three were generated natively with `gpt-image-2`; no post-generation type,
logo, border, or layout overlay was added.

## Preserved Rejections

| File | Hard-gate failure |
| --- | --- |
| `02-public-record-funding-file-wide-logos.png` | Added `PUBLIC RECORD` and repeated `$5,000`. |
| `02b-public-record-funding-file-wide-logos-repair.png` | Added `BUILD THE ARCHIVE` and repeated `$5,000`. |
| `03-reading-room-grant-card-square-logos.png` | Repeated the `$5,000` funding block. |

These candidates have valid dimensions, palettes, motifs, and provider
receipts. They remain in the second-round run for auditability but are not
selected for use.

## Provenance

The source ledger records four visually verified pre-1902 records retrieved
from Internet Archive on 2026-07-29:

- [1901 Canadian Pacific Railway survey profile, leaf n5](https://archive.org/details/31761108187790/page/n5/mode/1up)
- [1888 House of Commons debates, leaf n6](https://archive.org/details/31761116358672/page/n6/mode/1up)
- [1891 Census table, leaf n30](https://archive.org/details/31761119712784/page/n30/mode/1up)
- [1858 Geological Survey fossil plate, leaf n57](https://archive.org/details/31761075504423/page/n57/mode/1up)

Internet Archive supplies no explicit scan license for these four items. The
ledger makes no legal-status claim about the scans. Their structures informed
new artwork rather than raw-scan collage reproduction.

The second-round brand ledger records byte-identical local references for:

- Internet Archive Canada, SHA-256
  `16ac76f726e039b4fa9fb691117c42138bfa6f188cd4d30d190b7ce1da177bdb`;
- BC + AI Ecosystem, SHA-256
  `4249d992cdf6c5ed9480ea70f36ec50fb96f7888da3d05823958607117a33612`.

The marks were passed into native image generation as references, not
composited afterward.

## Verification

The final set and second variation round were verified with:

```bash
./.venv/bin/python prompts/bcai-fellowship-2026-07/verify-reading-room.py
./.venv/bin/python prompts/bcai-fellowship-2026-07/variations-r2/verify-variations-r2.py
./.venv/bin/python generate.py view bcai-fellowship-2026-07 --all-runs
./.venv/bin/python generate.py view bcai-fellowship-2026-07 --approved
./.venv/bin/python generate.py registry index --all-runs
./.venv/bin/python generate.py library
```

Closeout results:

- final five-asset launch set: passed;
- second round: three selected and three rejected from six provider calls;
- approved viewer: exactly five assets;
- Fellowship manifests: no missing images or malformed runs;
- global archive health: still reports unrelated historical missing assets
  outside this campaign.

## GitHub Relationship

Live GitHub review on 2026-07-30 found no open issue or pull request that
directly names the Fellowship, Internet Archive Canada, or Reading Room
campaign.

Adjacent but non-blocking work:

- [#335](https://github.com/WalksWithASwagger/rafiki/issues/335) defines a
  future privacy-safe model-output benchmark contract.
- [#336](https://github.com/WalksWithASwagger/rafiki/issues/336) is the blocked
  implementation follow-up for offline human-review benchmark reports.
- [#202](https://github.com/WalksWithASwagger/rafiki/issues/202), the
  CDN-backed approved-asset publishing research issue, is closed and recommends
  deferring publication.

The only open pull request at closeout is
[#383](https://github.com/WalksWithASwagger/rafiki/pull/383), an unrelated
TypeScript dependency upgrade.

## Next Explicit Gate

Using these assets in a website, social post, CDN, Canva, Notion, or other
public destination requires a separate publication/export instruction. A
second QA-passing logo-bearing composition would require another bounded
provider round; the two preserved wide logo attempts did not pass locked-copy
QA.
