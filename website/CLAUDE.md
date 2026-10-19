# Website

- Never edit `website/docs/`, `scripts/generate-docs.py` generates it from `website/content/` and the markers in
  `README.md`, `CONTRIBUTING.md` and `CHANGELOG.md`
- `website/content/index.md` is the integration page:
  - sections in the order of the home-assistant.io integration pages
  - covers installation parameters, options, removal, supported devices, entities, actions, data updates, use cases,
    examples, known limitations, troubleshooting
  - examples use the serial number `12345678` of the test data
- Design after home-assistant.io:
  - `website/src/css/custom.css` and the wrapped `website/src/theme/TOC/`
  - the integration card in `website/src/components/ProjectInfo/` reads `manifest.json` and `hacs.json`
