---
name: changelog
description: Rules for CHANGELOG.md entries, issue/PR links and release links. Use when adding a changelog entry, a release section or links.
---

# Changelog

- **Always strictly** follow [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), no deviations:
  - only `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`, in this order
  - releases as `## [x.y.z] - YYYY-MM-DD`, newest first
- Past tense
- Entries as short as possible: one sentence, what changed, no reasons, no explanations
  - at most about 15 words, details belong in the docs
  - few adjectives and adverbs, no filler words (`also`, `now`, `right away`, `instead of`)
  - only the effect the user sees, no implementation details
  - no sub-clauses with exceptions, no example lists
  - pattern verb + object (``Added the HVAC action `defrosting`.``), `Fixed` names the faulty behavior, not the cause
  - long: ``Showed the preset `away` right away, not only after the next update.``, short:
    ``Fixed the delayed preset `away`.``
- With every new entry, check the existing entries under `[Unreleased]` against the code
  - adapt, merge or remove entries that are outdated, contradicted or made redundant by the new one
- Identifiers in backticks
- Issues as `([Issue #25][issue-25])`, pull requests as `([PR #19][pr-19])`
- Issue and PR links are defined at the end of their release section, not at the bottom
  - a link that an older section already defines is reused, not defined again
- Releases are linked at the bottom, before `<!--end-->`:
  - `[Unreleased]` compares the latest release tag (no pre-release) with `HEAD`
  - each release compares its tag with the previous one
  - the first release links to its release tag
