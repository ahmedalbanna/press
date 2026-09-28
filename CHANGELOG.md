# Changelog

This file documents changes (current commit level since, no tagged releases yet).

---

## 28-09-2026 — 0.9.0

### Changed
- Press declares support for Frappe 17. `[tool.bench.frappe-dependencies].frappe` moves from `>=15.0.0,<17.0.0` to `>=15.0.0,<18.0.0`. The old upper bound was self-declaring the opposite: `parse_frappe_version` resolves that spec to the Frappe Version records it names, so it resolved to Version 15, 16 and Nightly while press was installing and migrating cleanly on 17.0.0-dev.

Compatibility was verified before the bound moved: an import probe of all 1006 press modules against a real Frappe 17.0.0-dev env gives 1005 importing and 1 pre-existing failure, byte-identical to the Frappe 16 result, and a throwaway bench completed `install-app press` and `migrate` at exit 0 with 440 patches, no orphaned DocTypes and 60 tests green. Details in [FRAPPE_17_ROADMAP.md](FRAPPE_17_ROADMAP.md).

- `requests` and `types-requests` move from `~=2.33.0` to `>=2.32,<3.0`. Frappe owns that pin and the two series do not overlap: 16 requires `~=2.33.2`, 17 requires `~=2.34.2`, so pinning press to either one made it uninstallable on the other.
- `press.utils.now()` and `press.utils.cache()` move to `press.utils.clock`, and `now` is renamed `now_utc`. `frappe.utils.now()` returns a *string* and `now_datetime` returns a naive datetime, so a third `now` on the same import line was a trap; `now_utc` says what it returns. `cache` is still re-exported from `press.utils`, so the two `get_minified_script` readers in that module and any external caller are unaffected. The module is `clock` and not `time` on purpose: importing a submodule binds it on the parent package, so `press/utils/time.py` would shadow the stdlib `time` that `press.utils` itself imports.
- `requires-python` stays at `>=3.10`. It describes what press's own code needs; the interpreter floor comes from the `frappe` dependency, which resolves per version (v15 allows 3.10, v16+ requires 3.14). Raising it to `>=3.14` would have made press uninstallable on a Frappe 15 bench, which the dependency range still claims to support.

### Fixed
- `get_new_site_options` raised on Frappe 16 and 17, so the new-site form had no version dropdown at all. It ordered by a bare `` `default` ``, which no longer parses: `order_by` is validated from Frappe 16 on, so a bare backticked field throws `Order By has invalid backtick notation` and the qualified `` `tabFrappe Version`.`default` `` form is required. This is the one place `Frappe Version.default` is read, so the flag did nothing on v17. The qualified form is accepted on 15 (no validation), 16 and 17, so this does not narrow compatibility. The existing test missed the regression because it only asserted inside a loop over `options["versions"]`, which never ran once the call raised; the new test asserts the resulting order, so it fails on every version if the form is reverted.
- `deploy_candidate/cache_utils.py` failed to import on *both* Frappe 16 and 17: `TypedDict` was declared in the pre-3.13 positional style, which raises `TypeError` at import time, taking down everything that imports it. Found by the v17 import probe, not by the test suite.
- `ProductTrialRequest` no longer imports `init_telemetry`, which is absent on both 16 and 17.
- `get_usage` returned `{"datasets": [], "labels": []}` where it is declared to return `list[UsagePoint]`. All three callers iterate the result and read attributes off each item, so a dict surfaced as `AttributeError: 'str' object has no attribute 'max'`. It now returns `[]`, and says so in its docstring.
- The Release Group dependency editor could not change `NVM_VERSION` for any version. A group takes its dependency versions from `Frappe Version.dependencies`, while the editor lists its choices from `Bench Dependency Version` filtered on `supported_frappe_version`. `NVM_VERSION` was offered only `0.39.1` while every Frappe Version defaults to `0.36.0` — a real nvm release, which `press/docker/Dockerfile` installs. Because the dashboard injects the group's current value into the option list, this did not look broken: the dropdown showed exactly one choice, the one already set. `BENCH_VERSION` on Nightly had the same shape (default `5.27.0`, nothing offered for it). Fixed by adding the missing options, and by a patch that derives the gaps from `Frappe Version.dependencies` rather than from a hand-written list, so the next version cannot land with one.
- Version 17 shipped without `Bench Dependency Version` rows, so a V17 group had no options to choose between. The same omission 0.8.0 fixed for Version 16.
- The cAdvisor-backed release group charts threw "We couldn't fetch metrics right now" whenever Prometheus returned no series. An empty result is a valid steady state — cAdvisor reports nothing for a container runtime it cannot enumerate — so it now renders an empty chart. `_get_cadvisor_data` returns a `(datasets, labels)` pair rather than `None`, so the caller has no sentinel to check.

### Note
- `hooks.py` still resolves the frappe.io login URL at import time, because that is the only place a `website_redirects` target can be produced. What changed is that a failure is logged instead of silently swallowed: the redirect falling back to `/` breaks frappe.io login for every customer with no other symptom, so a bare `except` around it hid the only diagnostic. `frappe.log_error` degrades to a print when no database is bound, which is the case that gets us there, so the fallback cannot raise in turn.
- `NVM_VERSION` is still declared as `0.36.0` on the `Frappe Version` records and in `Release Group.DEFAULT_DEPENDENCIES`, while `0.39.1` is also on offer. The patch adds the missing option rather than correcting the default, because that would change what every new group builds with. Moving the default to `0.39.1` is an operator decision.
- `ruff.toml` keeps `target-version = "py310"` and enables `DTZ003` only. The rest of the `DTZ` ruleset reports 327 pre-existing findings (`DTZ001/005/006/007/011` — naive `now()`, `date.today()`, strptime without `%z`), most of which are correct as written, and converting them is a separate change with per-call-site behaviour to work out.
- `test_every_pickable_version_offers_its_dependencies_in_the_editor` reads the database, so it needs the site's fixtures and patches to be current. On a site that has not migrated since 0.9.0 it fails, which is the intended signal.
- **Version 16 remains the default Frappe Version for new sites.** An earlier commit in this series set `Version 17` as the default; that is reverted here. `Frappe Version.default` only orders the new-site dropdown, so the two decisions are independent, and `Version 17` is still `status=Develop` — the same reason it is not the upgrade target. The four call sites that resolve "latest" as the highest-numbered `Stable` version (`press/press/doctype/site/site.py`, `site_group_deploy.py`, `api/marketplace.py`, `api/site.py`) are unaffected either way. Reverting it needs `restore_version_16_as_the_default` as well as the fixture change: dropping a patch from `patches.txt` does not un-apply it, so a site that already ran the flip keeps offering Version 17 until something clears the flag.
- `Version 17` is added with `default: 0`. The commit that added it appended a second `"default"` key to its fixture record instead of editing the existing one, leaving duplicate keys in the JSON; only the last one took effect, and `check-json` in pre-commit does not catch duplicates. Corrected here.
- `press.api.cookies` still fails to import on Frappe 17: `get_cookie_dict_from_headers` is gone from `frappe.oauth`. Pre-existing on both 16 and 17, found by the same import probe, and not touched here.

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
