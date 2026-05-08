# Branch Protection

Recommended protection for `main`:

- require pull requests before merging
- require the `CI / test` status check
- require branches to be up to date before merge
- block force pushes
- block deletions
- require conversation resolution

For autonomous PRs, keep maintainer spot checks enabled until at least 10
Rafiki PRs have passed review, CI, and audit-log recording without scope drift.
