#!/usr/bin/env -S uv run python
# Copyright 2025-2026 Michael Hacker
# SPDX-License-Identifier: Apache-2.0

"""Generate the Markdown pages of the Docusaurus website.

The integration page and the other hand-written pages are copied from ``website/content``. The donation,
contributing and changelog pages are copied from the marked sections of the Markdown files in the repository
root. All pages are written to ``website/docs``, which is not tracked by git.
"""

import re
import shutil
from pathlib import Path
from typing import ClassVar

ROOT: Path = Path(__file__).resolve().parent.parent
OUTPUT: Path = ROOT / "website" / "docs"
CONTENT: Path = ROOT / "website" / "content"
REPOSITORY: str = "https://github.com/superbox-dev/keba_keenergy"


class DocsGenerator:
    """Render the documentation pages into the Docusaurus docs folder."""

    # Links in the copied Markdown files, mapped to the generated pages, so Docusaurus checks them
    _LINKS: ClassVar[dict[str, str]] = {
        "(CHANGELOG.md)": "(changelog.md)",
        "(CONTRIBUTING.md)": "(contributing.md)",
        "(CLAUDE.md)": f"({REPOSITORY}/blob/main/CLAUDE.md)",
    }

    def __init__(self, output: Path) -> None:
        """Initialize the generator.

        Parameters
        ----------
        output
            Folder for the generated Markdown pages, replaced on every run.

        """
        self.output: Path = output

    def run(self) -> None:
        """Write all pages."""
        shutil.rmtree(self.output, ignore_errors=True)
        self.output.mkdir(parents=True)

        for page in sorted(CONTENT.glob("*.md")):
            shutil.copyfile(page, self.output / page.name)

        self._write_page("donation.md", self._front_matter("Donation", 90), self._extract("README.md", "donation"))
        self._write_page(
            "changelog.md",
            self._front_matter("Changelog", 70, hide_toc=True),
            "# Changelog",
            self._extract("CHANGELOG.md", ""),
        )
        self._write_page(
            "contributing.md",
            self._front_matter("Contributing", 80),
            "# Contributing",
            self._extract("CONTRIBUTING.md", "contributing"),
        )

    def _write_page(self, path: str, *blocks: str) -> None:
        content: str = "\n\n".join(block.strip("\n") for block in blocks if block)
        (self.output / path).write_text(f"{content}\n", encoding="utf-8")

    @staticmethod
    def _front_matter(title: str, position: int, *, hide_toc: bool = False) -> str:
        lines: list[str] = ["---", f"title: {title}", f"sidebar_position: {position}"]

        if hide_toc:
            lines.append("hide_table_of_contents: true")

        lines.append("---")
        return "\n".join(lines)

    def _extract(self, filename: str, marker: str) -> str:
        """Join all sections of a Markdown file between ``<!--start-marker-->`` and ``<!--end-marker-->``."""
        suffix: str = f"-{marker}" if marker else ""
        text: str = (ROOT / filename).read_text(encoding="utf-8")
        pattern: re.Pattern[str] = re.compile(rf"<!--start{suffix}-->(.*?)<!--end{suffix}-->", re.DOTALL)
        content: str = "\n\n".join(part.strip("\n") for part in pattern.findall(text))

        if not content:
            msg: str = f"No <!--start{suffix}--> section in {filename}"
            raise ValueError(msg)

        for link, target in self._LINKS.items():
            content = content.replace(link, target)

        return content


if __name__ == "__main__":
    DocsGenerator(OUTPUT).run()
