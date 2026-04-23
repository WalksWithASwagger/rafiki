# Product scope

## v1: CLI only

This repository (**Rafiki**) ships as a **command-line tool** (`npx rafiki` / `rafiki`; alias `npx image-gen`). There is **no HTTP API**, job queue, or multi-user auth in scope for the initial extraction.

Rationale:

- Keeps deployment and security surface minimal (one API key on the operator’s machine).
- Matches how the tool is used today: agents and humans run batch jobs from a checkout.
- A small FastAPI/Hono wrapper can be added later without forking generation logic if a service is needed.

## Out of scope (for now)

- Hosted image generation as a SaaS
- Per-seat billing, rate limiting, or shared usage logs across machines
- Tight coupling to any one knowledge base repository layout (consumers pass paths explicitly)

## Future extension

If you need Slack, webhooks, or an internal dashboard, add a thin HTTP layer that shells out to `generate.py` or imports it as a module—**do not duplicate** the Gemini client and prompt assembly.
