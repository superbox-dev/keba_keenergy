---
name: claude-md
description: Structure and style for CLAUDE.md files. Use when creating, rewriting, reviewing or shortening one.
---

# CLAUDE.md

## Structure

Always this order. Omit empty sections, never reorder or rename them.

```markdown
# CLAUDE.md

<One sentence: what the project is, stack, key dependencies.>

## Commands

## Rules

## Architecture

## Quality scale

## Documentation

## Changelog, versions and git
```

- Folder-only rules go to `<folder>/CLAUDE.md` (H1 with the area, then bullets)
- Task-specific workflows go to skills

## Style

- Only what the agent can't know: nothing from code, config or framework conventions, no duplicates
- Prefer enforcing a rule via linter/config over writing it down
- Bullets, max. 2 nesting levels, exceptions nested under their rule
- Fragments, not sentences, no trailing periods, no filler
- General rules over single cases
- Short reason only if a rule seems arbitrary
- **never**, **always**, **only** for strength, bold only for critical rules
- Identifiers, files, commands in backticks
- English
