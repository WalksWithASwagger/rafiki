# Branch Protection

Recommended protection for `main`:

- require pull requests before merging
- require the `test`, `secret-scan`, and `policy` status checks after all three
  are green on `main`
- require branches to be up to date before merge
- block force pushes
- block deletions
- require conversation resolution

`policy` is the stable repository check for GitHub issue traceability and sticky
`needs-human` / `blocked` gates. Applying these settings remains a separate,
explicitly approved maintainer action.

CodeQL and Dependency Review begin as reporting checks. A maintainer decides
whether to require them only after their initial pull-request and `main` runs
have succeeded.

For autonomous PRs, keep maintainer spot checks enabled until at least 10
Rafiki PRs have passed review, CI, and audit-log recording without scope drift.
