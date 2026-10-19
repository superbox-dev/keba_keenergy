---
name: quality-scale
description: Status and audit of the Home Assistant integration quality scale. Use when checking, auditing or improving quality scale rules.
---

# Quality scale

- Audit: check every rule against the code, including the rules under `## Quality scale` in `CLAUDE.md`
- Not applicable:
  - `entity-event-setup`: entities only use the coordinator
- Open:
  - `dynamic-devices`: devices are only detected on setup, a changed setup needs a reload
- Keep satisfied:
  - `brands`: brand images in the `home-assistant/brands` repository (`custom_integrations/keba_keenergy/`)
  - `reauthentication-flow` / `reconfiguration-flow`: keep both working
  - `diagnostics`: `diagnostics.py` redacts the host, the credentials, the serial number and the title
  - `discovery-update-info`: the zeroconf flow updates a changed IPv4 address, a configured hostname is kept
  - `stale-devices`: on setup, devices whose identifier is not in `coordinator.device_identifiers()` are removed
