# Spend Accounting

Rafiki reports local spend in the portal from two inputs:

1. `cost_estimate.amount` values already written into `run.json` manifests.
2. `config/pricing.json`, a public pricing profile for models where local
   image-output estimates are possible.

The estimate is for operator awareness, not invoice reconciliation. Provider
billing exports from OpenAI and Gemini remain the source of truth.

## Pricing Profile

`config/pricing.json` is tracked because it contains public rates, not secrets.
It records:

- `updated_at` for the pricing snapshot date
- model/provider names
- fixed per-image rates when the provider publishes them
- token rates when the provider requires token usage to estimate spend
- source URLs and notes

Update the profile when provider pricing changes. Do not put API keys, account
ids, invoices, or private billing exports in this file.

## Estimate Rules

| Source | Behavior |
|---|---|
| Manifest `cost_estimate.amount` | Counted as known local amount. |
| Gemini fixed output-image pricing | Estimated from `config/pricing.json` when manifest amount is missing. |
| OpenAI token-priced image models | Estimated only when a manifest includes output-token usage; otherwise left unpriced. |
| Dry runs | Recorded as `$0` actual spend with `potential_amount` when the pricing profile can estimate the real run. |
| Failed images | Not given output-image estimates unless a manifest already carries an amount. |

## Portal Fields

`GET /api/usage` returns both exact local manifest totals and pricing-profile
estimates:

- `archive.known_cost` totals only manifest amounts.
- `archive.estimated_cost` combines manifest amounts and pricing-profile
  estimates.
- `archive.estimated_cost.unpriced_images` is the count of successful images
  Rafiki still cannot estimate locally.

The Spend & Review Ops panel shows `archive.estimated_cost.amount` and keeps
the profile/manifest split visible in the small note under the dollar amount.

## Source Snapshot

The current tracked profile was refreshed on 2026-05-18 from:

- OpenAI API pricing: `https://developers.openai.com/api/docs/pricing`
- Gemini API pricing: `https://ai.google.dev/gemini-api/docs/pricing`
