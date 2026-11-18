# Contributing

<!--start-contributing-->

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Getting started

The project uses [uv](https://docs.astral.sh/uv/).

1. Set up the project with `./scripts/setup.sh`. This installs the dependencies, the [prek](https://prek.j178.dev)
   hooks and a git `pre-push` hook that validates release tags.
2. Start Home Assistant with `./scripts/develop.sh`.
3. Open <http://127.0.0.1:8123> in your browser.

## Pull requests

Pull requests are the best way to propose changes to the codebase.

1. Fork the repository and create your branch from `develop`. `main` is the release branch.
2. Update the documentation in `website/content/index.md` if you changed something user-visible.
3. Add an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md).
4. Make sure `./scripts/lint.sh` and `uv run pytest` pass.
5. Open the pull request against `develop`.

Never use real credentials, serial numbers or IP addresses of your heat pump in code, tests or issues.
Use the fake data in `tests/fixtures/`.

## Coding style

`./scripts/lint.sh` runs [ruff](https://docs.astral.sh/ruff/) (format and lint), [ty](https://docs.astral.sh/ty/),
yamllint and [rumdl](https://github.com/rvben/rumdl). See [CLAUDE.md](CLAUDE.md) for the project rules.

## AI assistant

The project only uses [Claude Code](https://claude.com/claude-code) as AI assistant. Its rules are in
[CLAUDE.md](CLAUDE.md), `tests/CLAUDE.md`, `website/CLAUDE.md` and the skills in `.claude/skills/`.

## Documentation

The documentation is a [Docusaurus](https://docusaurus.io) website in `website/` and needs Node.js.
The integration page is `website/content/index.md`:

```bash
./scripts/docs.sh        # build
./scripts/docs.sh start  # live reload
```

## Tests

Tests use [pytest](https://docs.pytest.org). **100% test coverage is enforced**, so every new code path needs a test.

```bash
uv run pytest
```

## Releases

Only maintainers create releases. Tags cannot be deleted, so a release must be correct before the tag is pushed.

1. Set the same version in `pyproject.toml` and `custom_components/keba_keenergy/manifest.json`.
   Use `X.Y.Z` for a stable release or `X.Y.ZbN` for a pre-release.
2. Rename `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) to `## [X.Y.Z] - YYYY-MM-DD` and add a new empty
   `## [Unreleased]` section above it. Pre-releases don't need a changelog section.
3. Merge the changes into `main`. Pre-releases are tagged on `develop` instead.
4. Run `./scripts/release.sh vX.Y.Z` from `main`, or `./scripts/release.sh vX.Y.ZbN` from `develop`.

`./scripts/release.sh` creates and pushes the tag only if `./scripts/check-release.sh` passes. The check verifies that
the tag, `pyproject.toml` and `manifest.json` have the same version and that stable releases have a changelog entry.
The same check runs again in the release workflow before anything is published.

Don't create tags manually and don't use `git push --no-verify` for tags.

## Report bugs

Report a bug by [opening a new issue](https://github.com/superbox-dev/keba_keenergy/issues/new/choose).
Great bug reports tend to have:

- A quick summary and/or background
- Steps to reproduce
- What you expected would happen
- What actually happens
- The Web HMI software version and the device hardware name
- Debug logs (remove credentials first)
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License

By contributing, you agree that your contributions will be licensed under the [Apache License][license].

[license]: https://github.com/superbox-dev/keba_keenergy/blob/main/LICENSE

<!--end-contributing-->
