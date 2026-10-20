# Website

- Never edit `website/docs/`, `scripts/generate-docs.py` generates it from `website/content/` and the markers in
  `README.md`, `CONTRIBUTING.md` and `CHANGELOG.md`
- Pages in `website/content/`: `sidebar_position` but no `title` in the front matter, the title comes from the `#`
  heading
- `website/content/index.md` is the integration page:
  - sections in the order of the home-assistant.io integration pages
  - covers installation parameters, options, removal, supported devices, entities, actions, data updates, use cases,
    examples, known limitations, troubleshooting
- Examples only with test data or placeholders, never real credentials, serial numbers or meter point numbers
- Preview image for shared links: `website/static/img/social-card.png` (1200 × 630, same layout in all projects)
- Design after home-assistant.io:
  - `website/src/css/custom.css` and the wrapped `website/src/theme/TOC/`
  - light mode by default, the right column at least `17.5rem` wide on smaller screens
  - the integration card in `website/src/components/ProjectInfo/` reads `manifest.json` and `hacs.json`
  - the brand logos are in `website/static/` (`logo.png`, `dark_logo.png`), the icon comes from
    `brands.home-assistant.io`
