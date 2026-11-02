---
name: issue
description: Rules for creating and updating GitHub issues (tickets). Use when asked to create, write, draft or update an issue or ticket.
---

# Issue

- Build the ticket from the matching template in `.github/ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`)
  - same title prefix, same labels, same headings in the same order
  - replace the placeholder texts of the template with the content
  - leave out optional sections without content (`Screenshots`, `Additional context`)
- As short as possible: facts only, few adjectives and adverbs, no filler, no reasons, no digressions
  - a few words or one sentence per section, steps to reproduce as short numbered items
- Every ticket ends with the section `## TODO`, a task list of the steps to close it (`- [ ] ...`)
  - short steps in the order of the work, e.g. fix, tests, docs, changelog
- Changes to a ticket go into the description, never into a new comment
  - outdated text is struck through (`~~old text~~`) and the new text follows, so the change stays traceable
  - done steps in the TODO list are checked (`- [x]`), dropped steps are struck through
- Tables are collapsed: `<details><summary>Name</summary>`, blank line, table, blank line, `</details>`
- US English
- Identifiers in backticks
- No credentials, serial numbers or public IP addresses, no unredacted logs
- Only create or update the ticket on GitHub (`gh issue create`, `gh issue edit`) when asked, otherwise show the draft
