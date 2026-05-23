# Spend Accounting

Rafiki reports local spend in the portal from three inputs:

1. `cost_estimate.amount` values already written into `run.json` manifests.
2. `config/pricing.json`, a public pricing profile for models where local
   image-output estimates are possible.
3. `data/billing-imports.json`, a gitignored local ledger created from provider
   billing exports or manual portal entries.

Provider billing exports from OpenAI and Gemini remain the source of truth.
When imports exist, the portal uses the imported provider-billing total as the
main spend number and keeps pricing-profile estimates visible as a fallback.

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

## Billing Imports

Use provider exports or a simple CSV/JSON ledger when you need the exact account
charge reflected locally:

```bash
python generate.py billing import ~/Downloads/openai-image-usage.csv --provider OpenAI
python generate.py billing summary
```

Supported import formats:

- `.csv` with headers such as `provider`, `model`, `amount`, `currency`,
  `date`, `images`, and `note`
- `.json` with a list, a single object, or an object containing `imports`,
  `entries`, `items`, `rows`, or `data`
- `.jsonl` with one object per line

Rows without a parseable amount are skipped. Re-importing the same file skips
duplicate rows. The ledger is stored at `data/billing-imports.json`, which is
ignored by git because invoices and account exports can be private.

The portal also has an **Add Billing Entry** form for one-off exact charges. It
writes to the same ledger through `/api/billing-imports`.

## Estimate Rules

| Source | Behavior |
|---|---|
| Manifest `cost_estimate.amount` | Counted as known local amount. |
| Gemini fixed output-image pricing | Estimated from `config/pricing.json` when manifest amount is missing. |
| OpenAI token-priced image models | Estimated only when a manifest includes output-token usage; otherwise left unpriced. |
| Billing import rows | Shown as provider billing and used as the main spend number when present. |
| Dry runs | Recorded as `$0` actual spend with `potential_amount` when the pricing profile can estimate the real run. |
| Failed images | Not given output-image estimates unless a manifest already carries an amount. |

## Portal Fields

`GET /api/usage` returns exact local manifest totals, pricing-profile estimates,
and provider billing imports:

- `archive.known_cost` totals only manifest amounts.
- `archive.estimated_cost` combines manifest amounts and pricing-profile
  estimates.
- `archive.spend` is the portal display total; it uses imported provider
  billing when available, otherwise `archive.estimated_cost`.
- `archive.estimated_cost.unpriced_images` is the count of successful images
  Rafiki still cannot estimate locally.
- `provider_billing` summarizes rows from `data/billing-imports.json`.

The Spend & Review Ops panel shows `archive.spend.amount` and keeps the
provider-import/profile/manifest split visible in supporting tiles.

## Source Snapshot

The current tracked profile was refreshed on 2026-05-18 from:

- OpenAI API pricing: `https://developers.openai.com/api/docs/pricing`
- Gemini API pricing: `https://ai.google.dev/gemini-api/docs/pricing`
