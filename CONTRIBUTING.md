# Contributing

Thanks for your interest in contributing to this GenesisAeon ecosystem
package!

## Getting started

1. Fork and clone the repository.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
   (or `.venv\Scripts\activate` on Windows).
3. Install in editable mode with dev dependencies:
   `uv sync` (or `pip install -e ".[dev]"`).
4. Run the test suite: `pytest` (or `uv run pytest`).

## Code style

- Format and lint with `ruff check` / `ruff format`.
- Type-check with `mypy src` (strict mode is enabled).
- Keep functions documented with concise docstrings.

## Diamond Interface

This package implements the GenesisAeon Diamond Interface
(`run_cycle`, `get_crep_state`, `get_utac_state`, `get_phase_events`,
`to_zenodo_record`) in `src/eml_utac_bridge/system.py`. Any change to
these methods' signatures or return shapes is a **breaking change** and
requires a MAJOR version bump (see `RELEASE_GUIDE.md`).

## Pull requests

- One logical change per PR.
- Add or update tests for any behavioral change.
- Update `CHANGELOG.md` under an `## [Unreleased]` section.
- Fill out the PR template (`.github/PULL_REQUEST_TEMPLATE.md`).

## Reporting issues

Please use the issue templates in `.github/ISSUE_TEMPLATE/` — they help us
triage bug reports vs. feature requests quickly.

## Scientific claims

This package formalizes a mathematical reduction (the EML operator
completeness result, Odrzywołek 2026) applied to the GenesisAeon
framework. If your contribution touches the reduction proofs, tree-depth
analysis, or any CREP/UTAC numerical claims, please cite the source and
clearly mark speculative vs. validated claims.
