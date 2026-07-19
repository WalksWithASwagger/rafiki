# AgentOpus MCP — generative video

Hosted MCP for **Agent Opus** (OpusClip's text/script → finished video product).
This is a **generation** surface, same family as Rafiki images + Floyo clips —
not the OpusClip long-form → shorts flywheel in `kk-kb/tools/media_pipeline/`.

Product page: https://agent.opus.pro/mcp  
App: https://agent.opus.pro  
FAQ: https://help.opus.pro/agent-opus/article/ao-faq  
Prompt guide: https://help.opus.pro/agent-opus/prompt-guide

## When to use which

| Need | Tool |
|------|------|
| Still images (Gemini / OpenAI, styles, batches, archive) | **Rafiki** local MCP (`MCP.md`) |
| Short ComfyUI / Floyo morphs, lip-sync, dry-run-first video | **Floyo** (`FLOYO.md`) |
| Narrative explainer / promo / faceless video from prompt or script | **AgentOpus MCP** (this doc) |
| Clip a meetup / YouTube long-form into shorts + schedule | **OpusClip** in kk-kb (`tools/opusclip_pipeline/`, `tools/media_pipeline/OPUS-MCP.md`) |

Do **not** use AgentOpus to caption or cut existing footage — that is OpusClip.

## Endpoint

```text
https://api.opus.pro/api/agent-mcp
```

Streamable HTTP + OAuth. No API key. Connection is scoped to the signed-in
AgentOpus account (styles, voices, brand anchors, credits).

## Install

### Cursor

Project or user `mcp.json`:

```json
{
  "mcpServers": {
    "agentopus": {
      "url": "https://api.opus.pro/api/agent-mcp"
    }
  }
}
```

Or use the product's **Add to Cursor** deeplink from https://agent.opus.pro/mcp.
Complete OAuth on first tool call.

### Claude Code

```bash
claude mcp add --transport http agentopus https://api.opus.pro/api/agent-mcp
```

### Codex CLI

```bash
codex mcp add agentopus --url https://api.opus.pro/api/agent-mcp
codex mcp login agentopus
```

## Tool surface (18 × `agentopus_*`)

Client tools are prefixed `agentopus_`. Core flow:

1. `whoami` — user, org, plan, credit quota (works on any plan; generation needs Pro+)
2. `list_styles` / `list_voices` / `list_image_models` / `list_assets` — catalog
3. `prepare_project` — prompt or script; voice, style, aspect ratio, duration, ≤8 anchors
4. `start_project` — queue render (**consumes credits**)
5. `get_video` — poll until result URL ready
6. `list_projects` — status + result URLs

Also: asset library (`upload_asset` / `register_asset` / `delete_asset`),
one-off project uploads, `customize_style`, `clone_voice` / `delete_voice`.

## Limits (product-stated)

- Max video length ~**600s**
- Bulk: **10** `start_project` calls per **5 minutes** per org (prepared projects kept)
- Asset library ≤**10** saved anchors; ≤**8** per video
- Image formats for anchors: png, jpeg, webp, gif
- Voice clone: **10–30s** non-instrumental sample

## HITL rules (KK)

- Always `whoami` before a spendy batch.
- Prefer a full script or detailed brief before `start_project` — AgentOpus
  auto-confirms brief/transcript/storyboard after ~5 minutes of idle if you
  walk away in the web app; treat MCP the same: review prepared intent.
- Brand logos / palette: upload anchors; do not rely on prompt-only brand
  description (product limitation).
- After a keeper lands, stills/thumbs for the KB still go through **Rafiki**;
  meetup short-form distribution still goes through **OpusClip / Buffer** in kk-kb.

## Related

- Local Rafiki MCP: [`MCP.md`](./MCP.md)
- Floyo video: [`FLOYO.md`](./FLOYO.md)
- kk-kb OpusClip clipping MCP: `kk-kb/tools/media_pipeline/OPUS-MCP.md`
- kk-kb image shim: `kk-kb/tools/image-gen/README.md`
