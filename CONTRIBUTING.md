# Contributing to MatchMind

This is a hackathon project with a hard deadline of **June 11, 2026**. Contributions are welcome — especially bug fixes, data quality improvements, and test coverage.

## Workflow

1. Fork the repo and create your branch from `dev` (not `main`).
2. Follow the branch naming convention in [docs/branching.md](docs/branching.md).
3. Make your changes with clear, focused commits.
4. Open a PR against `dev` — include the specific checkpoint or requirement your change addresses.
5. Ensure the `/api/health` endpoint still returns `{"status": "ok"}` after your changes.

## What We Need Most

- Bug reports via GitHub Issues (use the `bug` label)
- Data quality fixes for the `matches`, `venues`, and `local_businesses` seed data
- Additional language testing for the multilingual agent (see Feature WW-01 in [docs/features.md](docs/features.md))
- Frontend accessibility improvements

## What We Are NOT Merging Before June 11

- New features not in [docs/features.md](docs/features.md)
- Dependency upgrades that aren't security-critical
- Refactors that don't fix a confirmed bug

## Code Style

- **Python:** `ruff` for linting, `black` for formatting — run `ruff check .` and `black .` before committing
- **TypeScript/JSX:** `eslint` — run `npm run lint` in the `frontend/` directory
- No new comments unless the WHY is genuinely non-obvious

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
