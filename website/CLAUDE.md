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
  - only the light theme, no switch, colors of the home-assistant.io integration pages (e.g. `/integrations/unifi/`),
    except the links
  - `custom.css` is the same in all four projects, it has the light and the dark theme
  - the right column at least `17.5rem` wide on smaller screens
  - translucent header without blur, search as a rounded field with a `/` hint, `/` focuses it on every keyboard
    layout (`website/src/searchShortcut.ts`, the shortcut of the search plugin is off)
  - the integration card in `website/src/components/ProjectInfo/` reads `manifest.json` and `hacs.json`, shows the
    "My Home Assistant" badge below the logo and no changelog link
  - the brand logos are in `website/static/` (`logo.png`, `dark_logo.png`), the icon comes from
    `brands.home-assistant.io`
