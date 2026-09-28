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
- An App Source with no known versions is no longer rejected as incompatible. Versions come from GitHub, so an empty list means "could not read the tags"; the check now needs evidence before it refuses a deploy, and a known-incompatible source is still rejected.
- Release Group dependency bumps no longer append a second row for a dependency, which had locked affected groups out of dependency editing.
- `SiteGroupDeploy.set_latest_version` filtered on a lowercase `stable` status that matched no option, so it always resolved to nothing.
- Version lookups sort by `number` rather than `name`, and `limit=1` lookups pin an explicit `creation desc` order.
- `frappe.local.cookie_manager` is read defensively so a fresh request context cannot raise.
- `create_test_press_settings` seeds the offsite backup credentials that every Site Backup insert reads.
- The five scheduled jobs that selected a random slice of rows with `order_by="RAND()"` no longer raise `Invalid field format in Order By: RAND`. Frappe 16 validates `order_by` and accepts only plain field names, so all five were failing before doing any work. Randomness now goes through the query builder, which is not subject to that check.
- `TelegramMessage.get_one` no longer orders by MariaDB `FIELD()`, which Frappe 16 rejects, so the sender had been raising before reading a single queued message. Priority now ranks through a query builder `Case`.
- An unconfigured Telegram deployment no longer fails every send with `InvalidToken`, which `telegram.Bot` raises in the constructor before opening a connection. A missing token is now treated as "Telegram is off here" rather than a delivery failure, so the queue drains instead of retrying forever. `enqueue` is deliberately unchanged, so the misconfiguration stays visible rather than being silently swallowed.
- Release Groups created before the rq/gunicorn feature flags existed no longer keep the DocType defaults of 0. A Version 16 group could previously be built without `use_rq_workerpool` or with a single gunicorn thread per worker. Groups with any flag already set are left alone.

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
