# Changelog

This file documents changes (current commit level since, no tagged releases yet).

---

## 28-09-2026 — 0.8.0

### Added
- Version 16 bench dependency rows (Python 3.14, Node 24.12.0, nvm, pip, wkhtmltopdf) so the dependency picker is no longer empty for V16.

### Changed
- Version 16 is now the default Frappe version for new Release Groups.
- Press runs on Frappe 16 and Python 3.14.3.
- `frappe-mcp` and `semgrep` moved to the optional `mcp` and `audit` extras.
- `python-telegram-bot` upgraded to v21; sending is now driven through `asyncio.run`.

### Fixed
- `ProductTrialRequest` no longer imports `init_telemetry` from `frappe.utils.telemetry`, which Frappe 16 removed. This mattered more than a failing page: `remove_orphan_doctypes` deletes the DocType record of any controller that fails to import, so the migrate silently dropped the DocType.
- Release Group dependency bumps no longer append a second row for a dependency, which had locked affected groups out of dependency editing.
- `SiteGroupDeploy.set_latest_version` filtered on a lowercase `stable` status that matched no option, so it always resolved to nothing.
- Version lookups sort by `number` rather than `name`, and `limit=1` lookups pin an explicit `creation desc` order.
- `frappe.local.cookie_manager` is read defensively so a fresh request context cannot raise.

### Note
- The MCP endpoint is unavailable on Python 3.14 until `frappe/mcp` relaxes its `pydantic<2.12` pin. Everything else, including the incident support agent that imports from `press.mcp`, works without it.

---

## 03-02-2026

### Changed
- Introduced stricter app versioning requirements for all Frappe apps.
- All apps (Marketplace and private) must now:
  - Include a `pyproject.toml` file
  - Declare a bounded Frappe dependency under `[tool.bench.frappe-dependencies]`.
  - Support is only added for NPM based versioning, 

### Breaking Changes
- Apps without a `pyproject.toml` file will fail validation.
- Apps using unbounded Frappe version ranges (e.g. `^`, `~`, or single-sided constraints) are rejected.

### Note on version syntax

Frappe app version constraints are validated using **NPM-style semantic versioning** (`NpmSpec`), in favour of internal frappe applications such as CRM and helpdesk.

As a result:
- Version ranges must follow **NPM semver syntax**
- Python-style version specifiers (PEP 440), such as `~=`, are **not supported**

### Relevant links
https://github.com/frappe/press/issues/4809

### Example
```toml
[tool.bench.frappe-dependencies]
frappe = ">=16.0.0-dev,<17.0.0-dev"
