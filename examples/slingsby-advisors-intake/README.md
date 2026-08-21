# Slingsby Advisors Intake (public templates)

Fill these **locally**. Copied files live under gitignored `assets/slingsby/`
and are never committed.

```bash
mkdir -p assets/slingsby/likeness assets/slingsby/wardrobe \
  assets/slingsby/style-refs assets/slingsby/proposal-refs
cp examples/slingsby-advisors-intake/CONSENT.example.md assets/slingsby/CONSENT.md
cp examples/slingsby-advisors-intake/NOTES.example.md assets/slingsby/NOTES.md
```

Then drop authorized portraits into `assets/slingsby/likeness/` and run:

```bash
bash scripts/slingsby-proposal-generate.sh --status
bash scripts/slingsby-proposal-generate.sh --execute
```

Do not scrape LinkedIn, HFF, CreativeMornings, or Tanya's Shoru photography
set. Public painting refs may already be cached locally in
`assets/slingsby/style-refs/` for style plates only.
