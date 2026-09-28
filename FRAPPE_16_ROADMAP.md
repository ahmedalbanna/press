# Press — Frappe 16 Upgrade Roadmap

Target: Press `0.7.0` on Frappe `15.121.0` -> Press on Frappe `v16.35.0` (stable).
Non-targets: stay on 15 (tech debt), move to 17 (`develop` is `17.0.0-dev`, unstable).

Date: 2026-09-28. Bench: `/home/press/benches/control` (apps: `frappe`, `press`).

## 0. Baseline (verified)

- `press/__init__.py:4`: `__version__ = "0.7.0"`. `press/patches.txt:153-174` already has `v0_8_0` block. Version bump deferred.
- `pyproject.toml:92`: `frappe = ">=15.0.0,<17.0.0"` — already admits 16.
- `pyproject.toml:14`: `requires-python = ">=3.10"`.
- `press/fixtures/frappe_version.json`: `Version 16` Stable/public, Python 3.14 / Node 24.12.0 / Bench 5.31.0. `Version 15` still `default=1`.
- Control: `bench 5.29.0`, Python 3.12.3 (3.14 available), Frappe `version-15` branch.

## Phase 1 — P0 breakage fixes (on v15, before upgrade)

Goal: code that breaks silently or loudly on v16.

1.1 `has_permission` explicit return. v16 denies implicit `None`.
- `press/hooks.py:141-175` (registration list)
- `press/press/doctype/team/team.py:1955`
- `press/press/doctype/invoice/invoice.py:1706`
- `press/press/doctype/app_release/app_release.py:489`
- Reference good: `press/overrides.py:117-138`
- Done when: every code path returns explicit `True`/`False`. No fall-through.

1.2 Default sort `modified` -> `creation`.
- Audit all `get_all`/`get_list`/`get_value` without explicit `order_by`, e.g. `press/api/site.py:778`.
- Add `order_by="modified desc"` where recency-by-modification is intended.
- Done when: `grep -rn "get_all\|get_list" press/ --include="*.py" | grep -v order_by` reviewed.

1.3 `uploadfile` removal + POST-only methods.
- `press/hooks.py:472`, `press/overrides.py:18-57` (override is `upload_file`, correct).
- Verify no caller hits `/api/method/uploadfile` and dashboard upload calls use POST.
- Verify no shorthand RPC (`cmd` without full path, warned in `frappe/handler.py:134` v15).

1.4 Dead version lookup.
- `press/press/doctype/site_group_deploy/site_group_deploy.py:65`: `{"status": "stable"}` lowercase matches nothing. Fix to `Stable` or remove.

## Phase 2 — Dependency + hook compat

2.1 Pinned deps (`pyproject.toml`).
- `:42` `requests<2.32` conflicts with v16 `requests>=2.32`. Bump + `:70` `types-requests<2.32`.
- `:49` `tomli==2.0.1` -> conditional (`tomllib` on 3.11+). Callers: `press/api/github.py:21,474-475,623-624`, `press/press/doctype/app_release/app_release.py:15,624`, `press/press/doctype/deploy_candidate/utils.py:90`.
- `:97` `Werkzeug==3.1.3` — keep manually in sync with framework + moto.
- `:60` `setuptools==80.9.0`, `:14` `requires-python>=3.10` -> raise floor to `>=3.11` (v16 needs 3.11+; tenants use 3.14). Update classifiers `:20-22`.
- Re-check strict pins: `ansible==3.4.0`, `boto3==1.39.14`, `dnspython==1.16.0`, `docker==6.1.2`, `oci==2.180.0`, `paramiko==3.3.1`, `stripe~=2.56.0`.

2.2 `frappe.local.*` and response mutation.
- `press/overrides.py:36-37,75-83,165`, `press/saas/api/__init__.py:70-78`, `press/api/cookies.py:14-17`, `press/api/account.py:183,287,377`, `press/api/client.py:166,248,313-318`.
- Response mutation: `press/api/marketplace.py:508-509`, `press/api/oauth.py:60,68-69,102-123`, `press/api/google.py:44-48,97-132`, `press/api/site.py:1759-1760`.
- Handler imports: `press/overrides.py:10,40-41`, `press/api/client.py:12` (`frappe.handler` moved in develop).
- Done when: smoke login, OAuth, upload, SaaS site-name flows pass on v16 bench.

2.3 Cache + query builder.
- `redis_cache`/`site_cache`: `press/utils/__init__.py:28,519,1037,1079,1127`, `press/press/doctype/site_update/site_update.py:17,901`, `press/api/access.py:9-10`, `press/api/blog.py:10,38`.
- `frappe.qb` deep imports: `press/api/site.py:15-16`, `press/api/incident.py:2`, `press/press/doctype/agent_job/agent_job.py:1257`, `press/guards/role_guard/*.py`, `press/press/doctype/site_version_audit/site_version_audit.py:8`.
- `CustomUser.get_list_query`: `press/overrides.py:163-210`.
- `!= None` filters now `IS NOT NULL` — audit logic that depended on old behavior.

2.4 Hooks (`press/hooks.py`).
- `:481` `override_doctype_class`, `:484` `on_login`, `:486-491` `before_request`/`before_job`, `:501` `auth_hooks` (`press/auth.py:87`), `:503` `page_renderer` (`press/metrics.py:14-18,73-80`), `:505` `export_python_type_annotations`, `:507-509` `default_log_clearing_doctypes`, `:531-567` `persistent_cache_keys`, `:569-573` `before_migrate`/`after_migrate`, `:214-442` scheduler + 6-field cron `:340,349`.

2.5 Frontend.
- `dashboard/package.json:33` `frappe-ui 0.1.277` exact pin, `:74` `vite 8.0.1`. Bump in lockstep with v16 desk. Audit `createResource`/`createListResource` usage.

## Phase 3 — Version pins + defaults

3.1 `press/fixtures/frappe_version.json`.
- Keep V16 row as-is (correct). Do not flip `default=1` to V16 until tenant benches pass.
- Fix `Nightly` `number: 15` duplication with `Version 15`. Renumber (e.g. 99) or document.
- Add missing V16 rows to `bench_dependency.json` (`PYTHON_VERSION`, `NODE_VERSION`, `NVM`, `PIP`, `WKHTMLTOPDF`). Only `BENCH_VERSION` has V16->5.31.0 today.
- Update `FrappeVersion.DEFAULT_DEPENDENCIES` (`press/press/doctype/frappe_version/frappe_version.py:10-16`): bench `5.25.1` -> `5.31.0`, Node 18.16.0 / PY 3.11 are V15-era.

3.2 `name desc` -> `number desc`.
- `press/api/site.py:1821`, `press/press/doctype/site/site.py:404`, `press/api/marketplace.py:400`. Already correct at `press/api/site.py:1201,5479`, `press/press/doctype/site/site.py:5479`, `press/api/marketplace.py:297`, `press/api/bench.py:249`.

3.3 Patch asymmetry.
- `press/patches/v0_8_0/bump_v16_bench_version_to_5_31_0.py` filters `enabled=1`; V15 variant does not. Align. Add missing `test_bump_v16_*` (only V15 test exists).

3.4 Control tooling.
- `bench 5.29.0` -> `5.31.0` to match fixture + patches.

## Phase 4 — Control bench upgrade (DONE 2026-09-28: Python 3.14.3 + frappe 16.35.0)

**Completed:** `migrate --skip-failing` on `press.localhost` -> EXIT 0 under frappe `16.35.0` / Python `3.14.3`.

Rollback point if needed: `git -C apps/frappe checkout version-15` (was `4fa1b14`), then `uv pip install -e apps/frappe`.

### Runbook gotcha: clear Redis before migrating a major version
The first v16 migrate failed with
`module 'frappe.cache_manager' has no attribute 'build_domain_restriced_doctype_cache'`.
That function name came from **v15's cached `app_hooks` in Redis** (v15 shipped the typo
`restriced`, v16 renamed it to `restricted`). The cached hook list outlives the code change,
so `get_hooks("doc_events")` still resolved the old name. `press.overrides.before_after_migrate`
only calls `frappe.cache.flushall()` in `after_migrate`, which is too late.

Always flush cache and queue before a major-version migrate:
```bash
redis-cli -p <cache_port> FLUSHALL
redis-cli -p <queue_port> FLUSHALL
bench --site <site> migrate --skip-failing
```
Press's persistent cache keys (`press/hooks.py:531-567`) are unaffected, but the stale
`app_hooks` value is exactly the kind of thing to clear first.

## Final state (2026-09-28)

Control bench `/home/press/benches/control` is live on **Python 3.14.3 + frappe 16.35.0**:
- `migrate --skip-failing` EXIT 0
- services restarted and confirmed on 3.14 (`supervisorctl restart press-bench-web: press-bench-workers: press-bench-build-worker:... press-bench-sync-worker`)
- `http://press.localhost:8003/` -> 200, `/api/method/ping` -> 200, scheduler healthy
- `community.mysql 5.0.2` installed to `~/.ansible/collections` for the two roles that need it

### Open follow-ups
1. **Telegram live round-trip** — `press/test_telegram_utils.py` now covers the v21 async rewrite offline (7 tests: truncation, parse mode, topic routing, no-op, error swallowing, `reraise`, `get_username`). What is *not* covered is an actual call to the Bot API: no token is configured on `press.localhost` (`tabTelegram Group` is empty), so someone with a real token should send one alert.
2. **`press/tests/test_audit` + 4 errors in `press/api/tests/test_bench`** — pre-existing, not introduced here.
3. **Bench CLI 5.29.0 -> 5.31.0** — still deferred (system pip is PEP 668 externally-managed). The control CLI works; the fixture pin matters for tenant bench images.
4. **`datetime.utcnow()` deprecation** — 5 call sites in `press/utils/__init__.py:351-357` (cache expiry) and `press/press/report/aws_s3_storage_cost/aws_s3_storage_cost.py:110,144`. Warning only on 3.14; removal lands in 3.15. The cache ones are safe to convert (both sides naive); the S3 report is not worth the risk.
5. **Default version flip** — `Version 15` still has `default=1`; flip to V16 only after tenant V16 benches bake.
6. **Press `0.7.0` -> `0.8.0`** — deferred by request.

## Test results on 3.14.3 + frappe 16.35.0 (2026-09-28)

| Module | Result |
|---|---|
| `press.press.doctype.frappe_version.test_frappe_version` | 1/1 OK |
| `press.incident_management.support_agent.test_investigation` | 13/13 OK |
| `press.press.doctype.site_group_deploy.test_site_group_deploy` | OK |
| `press.api.tests.test_bench` | 29 run, 25 pass, 1 skipped, 4 errors — all the pre-existing `App frappe can be added only once` (`release_group.validate_duplicate_app`), previously confirmed on the pristine tree |
| `press.tests.test_audit` | 7 errors — pre-existing, `validate_app_version` throws when an `App Source` has no `versions` rows |

### Second real v16 breakage: silent DocType deletion
`frappe/model/sync.py:remove_orphan_doctypes` calls `get_controller()` for every DocType and
**deletes the DocType record** if the controller raises `ImportError` or `DoesNotExistError`.
Press hit this: `press/saas/doctype/product_trial_request/product_trial_request.py:16` imported
`init_telemetry` from `frappe.utils.telemetry`, which v16 removed. The controller failed to
import, so the migrate **silently dropped the `Product Trial Request` DocType record**, and
`test_bench` then failed at test *discovery* with `DocType Product Trial Request not found`.

Press has its own `init_telemetry` in `press/utils/telemetry.py:14`; the import was simply
pointed at the wrong module. Fixed to import from `press.utils.telemetry`, and the DocType
record was restored by re-running the migrate.

**Lesson:** a broken controller import does not just raise — it makes the framework delete your
DocType. Always check the `Orphaned DocType(s) found:` line in the migrate output. The other
orphans reported in that run (`Newsletter`, `Blog Post`, `Energy Point*`, `Dropbox Settings`,
`Google Drive`, `Transaction Log`) are framework modules that v16 genuinely extracted into
separate apps, so their removal is expected.

## Phase 4 — Control bench upgrade (env 3.14 DONE, frappe switch NEXT)

Status 2026-09-28: control env is on **Python 3.14.3** and boots. `press.overrides`, `press.runner`, `press.mcp`, `press.telegram_utils` all import. Still on frappe `15.121.0`; the `v16.35.0` switch is the next step.

Verified on 3.14 + v15:
- `bench --site press.localhost migrate --skip-failing` -> EXIT 0
- `test_frappe_version` 1/1 OK (covers T9)
- `test_investigation` 13/13 OK (covers the `press.mcp` refactor)
- `test_audit` 7 errors — **pre-existing**, confirmed identical on the stashed pristine tree. Cause: `release_group.validate_app_version` throws when an `App Source` has no `versions` rows (`all([])` is `True`), which is the state in this environment.

Ansible: `ansible==3.4.0` -> `ansible-core>=2.18,<2.19`. 2.18 is deliberate: it is the newest core whose `TaskExecutor._poll_async_result(self, result, templar, task_vars=None)` still takes a plain result dict, which is the exact signature `press/runner.py:53-64` monkey-patches. ansible-core 2.21 changed it to `UnifiedTaskResult`, which would require rewriting the async-progress patches. Verified `PlaybookExecutor`, `InventoryManager`, `DataLoader`, `Playbook`, `ActionModule`, `CallbackBase`, `Display`, `VariableManager` all still exist in 2.18.

**Outstanding:** only `press/playbooks/roles/install_tcmalloc_udf` and `mariadb_prepare_replica` use `community.mysql`, which is no longer bundled. Install with `ansible-galaxy collection install community.mysql` (default `~/.ansible/collections` path works) before those two roles run.

Cutover order (required: env first, frappe second):
- Bench CLI 5.29.0 -> 5.31.0: DEFERRED. System pip is PEP 668 externally-managed; forcing risks OS python. Fixture pin is for tenant bench images, control CLI still functional.
- Env Python 3.11 -> 3.14: BLOCKED 2026-09-28, ROLLED BACK to 3.11.14 (migrate-env EXIT:0; press 0.7.0 + frappe 15.121.0 + pyOpenSSL import OK; playwright 1.55.0/greenlet 3.5.6 installed on 3.11 too). Blockers recorded: (1) playwright→greenlet FIXED by our bump; (2) frappe-mcp 0.1.1 → pydantic<2.12 → pydantic-core 2.33.2 unbuildable on 3.14 (PyO3 0.24.1 cap; Rust + ABI3 flag tried) — needs upstream fix. Control plane restart-safe again.
- Frappe `version-15` -> `v16.35.0` tag: DEFERRED behind env. Tag verified locally `012667b`. Requires Python >=3.14 in every v16 tag (checked v16.0.0/5/10/20/30/35), so env 3.14 is a hard precondition.

### Blockers removed 2026-09-28

1. `playwright==1.49.1` -> `==1.55.0` (its pinned `greenlet==3.1.1` has no cp314 wheel).
2. `frappe-mcp` moved from required dependencies to the optional `mcp` extra. It pins `pydantic~=2.11.7` -> `pydantic-core==2.33.2` (PyO3 0.24.1 caps Python 3.13; no cp314 wheel; unbuildable from source). `frappe-mcp` only uses `BaseModel`/`ValidationError`, and press has zero direct pydantic imports, so the pin is pure overhead.
   - `press/mcp/__init__.py` now imports `frappe_mcp` defensively and falls back to `_MCPUnavailable`, a no-op stand-in whose `.tool()`/`.register()` are identity decorators. Required because `press.mcp` is imported as a parent package by the incident support agent (`collectors.py:187,382,458` -> `press.mcp.tools.telemetry.clients`) and by the tool modules that do `from press.mcp import mcp`.
   - With the extra installed, `mcp` is still a real `frappe_mcp.MCP` and `@mcp.register()` still exposes the endpoint — verified both paths.
   - Consequence: the MCP endpoint is unavailable on Python 3.14 until `frappe/mcp` relaxes its pydantic pin. It is opt-in behind `Press Settings.enable_mcp` and is the only consumer of the library.
   - Verified: `press.mcp`, `telemetry.clients`, tool modules and `support_agent.collectors` all import with `frappe_mcp` blocked; `test_investigation` 13/13 OK.

1. `bench update` control to `v16.35.0` tag (not `develop`). Python 3.14 env, Node 24.
2. `bench --site press.localhost migrate --skip-failing` — DONE 2026-09-28, EXIT:0. Sanity-check warning `'NoneType' object has no attribute 'group'` is pre-existing chromedriver/Chrome mismatch (`press/sanity.py:64`), non-fatal, unrelated to T1-T9.
3. `bench --site press.localhost run-tests --app press` for touched modules — PARTIAL 2026-09-28: `test_frappe_version` PASSED (1 test, OK). `test_bump_v15`: 2/3 pass; `test_patch_bumps_outdated_group_to_5_31_0_and_shows_update_available` errors in `validate_duplicate_app` ("App frappe can be added only once") — confirmed PRE-EXISTING by re-running on stashed pristine tree (same error, our changes stashed). `allow_tests` enabled on press.localhost. Test env: installed `moto 5.2.3`, `Faker 23.2.0`, `freezegun 1.2.2`; kept `cryptography 45.0.7` (50.x breaks pyOpenSSL `GEN_EMAIL`).
4. Manual smoke: login, dashboard, site creation picker (V15 default vs V16 latest), upload, billing, agent jobs poll.
5. Rollback: restore DB + `git checkout version-15` for frappe + `bench switch-to-branch` if migrate fails. Do not flip V16 `default=1` until smoke passes.

## Dependency modernization (2026-09-28, required for Python 3.14 / Frappe 16)

Frappe 16 hard-requires `cryptography~=50.0.0` + `pyOpenSSL~=26.4.0` + Python 3.14. That cascades into several legacy pins. Every change below was needed to make the control env import cleanly on 3.14.

| Change | Reason |
|---|---|
| `playwright` 1.49.1 -> 1.55.0 | 1.49.1 pins `greenlet==3.1.1`, which has no cp314 wheel and fails to build (PyO3 C++ errors on 3.14) |
| `frappe-mcp` -> optional `mcp` extra | pins `pydantic<2.12`; `pydantic-core 2.33.2` uses PyO3 0.24.1 (caps Python 3.13). Only consumer is the opt-in MCP endpoint |
| `docker` 6.1.2 -> `>=7.1.0` | 6.1.2 uses `cryptography.algorithms.TripleDES`, removed in cryptography 42+ |
| `paramiko` 3.3.1 -> `>=3.5.0` | same `TripleDES` removal (no direct press usage; ansible needs it) |
| `oci` 2.180.0 -> `>=2.187.0` | 2.180.0 caps `cryptography<47`, incompatible with v16's 50.x. 2.187.0 allows `<51` |
| `pyOpenSSL` 23.2.0 -> `~=26.4.0` | match framework; 23.x needs `cryptography<42`. Also removes the need for the `GEN_EMAIL` dev cap |
| `stripe` 2.56.0 -> `>=11.0.0` | 2.56 imports `stripe.six.moves`, broken on 3.12+. Verified every `stripe.*` attribute press uses is unchanged in v11 |
| `python-telegram-bot` 13.15 -> `>=21.0` | 13.15 imports `imghdr` (removed 3.13) and vendors urllib3 with absolute imports, so it also needed `urllib3<2` — which collides with `oci>=2.187`'s `urllib3>=2.6.3` |
| `semgrep` -> optional `audit` extra | semgrep needs `urllib3>=2`. Press only ever shells out to the `semgrep` CLI, and the audit already reports a clear `semgrep_unavailable` result when the binary is absent |
| dev `cryptography` cap `~=45.0` -> `~=50.0.0` | the old cap existed only to prop up pyOpenSSL 23 |

### Telegram code migration (13.15 -> 21.11.1)
Telegram alerting is load-bearing (10+ `TelegramMessage.enqueue` sites, a 5-minute scheduler, and the `press/api/telegram.py` bot webhook), so it was upgraded rather than removed. v20+ is async, so `press/telegram_utils.py` changed:
- `telegram.MAX_MESSAGE_LENGTH` -> `telegram.constants.MessageLimit.MAX_TEXT_LENGTH`
- `telegram.ParseMode` -> `telegram.constants.ParseMode`
- `timeout=3` on `send_message` -> `HTTPXRequest(connect_timeout/read_timeout=3.0)`, since v21 dropped the parameter
- `send_message` is a coroutine, so sends run via `asyncio.run` with the bot opened and closed inside that loop (the HTTPX pool is loop-bound)
- `Bot.username` is now a property populated by the async `initialize()`, so `respond()` calls a new `get_username()` helper

**Not verified by tests:** the actual Telegram network round-trip. Needs a live smoke test against a real bot token.

1. Enable V16 Release Groups for new benches first. Keep V15 default until bake-in.
2. Flip `default=1` V15 -> V16 only after 1-2 successful tenant bench builds + site updates.
3. Cheap future-proofing (works on both, required for 17):
   - `frappe.flags.in_test` -> `frappe.in_test` (~15 sites).
   - `generate_hash("name", n)` -> keyword/no-arg (`press/api/account.py:348`, `press/api/developer/marketplace.py:142`, `press/api/developer/saas.py:66`).
   - `FrappeTestCase` -> `IntegrationTestCase`/`UnitTestCase` (~10 modules).
   - `frappe.db.commit()` audit: must not be in `doc_events` handlers (`press/hooks.py:181`).

## Acceptance criteria (gate: T1/T2/T5)

- [ ] T1, T2, T5 fixed, ruff + relevant `run-tests` pass on v15. Gate for control upgrade.
- [ ] Control bench on `v16.35.0` + `bench 5.31.0`, migrate clean.
- [ ] New Release Group can build on V16 (Python 3.14 / Node 24.12.0 image).
- [ ] No `requests`/`Werkzeug` version conflict on install.
- [ ] `default=1` decision recorded (stay V15 or flip V16).
- [ ] Press version bump `0.7.0` -> `0.8.0` done separately (out of scope here).

## Ticket breakdown (agreed 2026-09-28: split T6, split T7, keep all, gate T1/T2/T5)

Gate (must land before control upgrade):

- T1 — has_permission explicit returns. DONE 2026-09-28 (verified, no code change). All 11 hooks return explicit `True`/`False`/bool: `press/overrides.py:117-138`, `press/press/doctype/team/team.py:1955-1970`, `press/press/doctype/invoice/invoice.py:1706-1725`, `press/press/doctype/app_release/app_release.py:489-503`, `press_role.py:260-268`, `account_request.py:401-410`, `team_member_resource.py:89-90`, `press_webhook_attempt.py:31-34`, `marketplace_app_plan.py:31-47`, `server_firewall.py:192-194`, `support_access.py:329-334`. `py_compile OK`.
- T2 — order_by audit. PARTIAL 2026-09-28. `get_last_doc` wrapper (`press/utils/__init__.py:339`) already `creation desc` — safe. Backup listing (`press/api/site.py:771-785`) and `site_update.py:340,1028` already explicit — safe. Fixed 5 `limit=1` lookups to explicit `creation desc`: `press/api/bench.py:725,731`, `deploy_candidate.py:139,145,520`. Remaining 2300+ `get_all` without `order_by` are unique-filter or list-all (no latest-singleton logic); full sweep deferred to T7a.
- T3 — upload + RPC. DONE 2026-09-28 (verified, no code change). Dashboard `dashboard/src/controllers/fileUploader.js:67` uses `POST /api/method/upload_file`; no `uploadfile` callers in code; `dashboard/src/controllers/call.js:25` uses full `/api/method/${method}` path.
- T4 — dead version lookup. DONE 2026-09-28 (1-line fix). `press/press/doctype/site_group_deploy/site_group_deploy.py:65` `stable` -> `Stable`. `py_compile OK`.
- T5 — dependency unpins. DONE 2026-09-28 (5 edits). `pyproject.toml`: `requests<2.32` -> `~=2.33.0` (matches frappe v15 `~=2.33.0` + v16.35 `~=2.33.0`), `types-requests` same, `setuptools==80.9.0` -> `~=81.0` (matches build-system), `Werkzeug==3.1.3` -> `==3.1.6` (matches framework v15/v16), classifiers add 3.13/3.14. `tomli` kept (needed for 3.10 floor). TOML parses OK.

Follow-ups (can overlap upgrade testing):

- T6a — auth surface of `frappe.local`. DONE 2026-09-28 (1 edit + verify). `press/api/cookies.py:14` `frappe.local.cookie_manager` -> `getattr(..., None)` (AttributeError-safe on fresh Local). Verified no-change: `press/saas/api/__init__.py:70-78` site/team context + lambdas, `press/auth.py:87-119` path gate (`upload_file` correct, full-path RPC), `press/overrides.py:75-83` team/system_user binding, `press/api/client.py:630` already `hasattr`, `press/api/account.py` login_manager/team uses are standard.
- T6b — upload/response mutation + handler imports. DONE 2026-09-28 (verified, no code change). `frappe/handler.py` exists in v16.35 (`is_whitelisted`, `run_doc_method` imports stable: `press/overrides.py:10`, `press/api/client.py:12`). Response mutation (`frappe.local.response.type/location`, dict-style `["http_status_code"]`) consistent across `press/api/oauth.py:60-124`, `google.py:44-137`, `saas.py:274-275`, `site.py:1759-1760,2614-2615`; `frappe.response` == `frappe.local.response` proxy. Uploaded-file pair (`press/overrides.py:36-37` sets, `marketplace.py:508-509`/`account.py:822-824` reads) intact.
- T7a — cache + query builder. DONE 2026-09-28 (verified, no code change). `frappe/utils/caching.py` exists in v16.35. `@site_cache` uses arg-less or hashable str args (`utils/__init__.py:519,1037`, `site_update.py:901-902`) — safe. `@redis_cache` without `user=` (`blog.py:38`, `server.py:450,546,559,572`, `analytics.py:792+`, `utils:1079,1127`) matches v15 behavior; cross-team keying unchanged, out of scope. qb imports (`frappe.qb.DocType`, `query_builder.functions/terms/custom`, `pypika.queries.QueryBuilder` in `client.py:18`) all present in v16 (PyPika fork pinned). `CustomUser.get_list_query` (`overrides.py:163-168`) standard qb. `access.py:9` `redis_cache(user=True)` + `validate_argument_types` signatures stable.
- T7b — hooks + scheduler. DONE 2026-09-28 (verified, no code change). v16.35 still reads: `page_renderer` (`path_resolver.py:get_custom_page_renderers`, same `can_render`/`render` interface as `press/metrics.py:14-80`), `auth_hooks` (`auth.py:751`), `override_doctype_class` (`base_document.py:110`), `override_whitelisted_methods` (`__init__.py:1579`), `before_request`/`before_job`, `persistent_cache_keys`, `default_log_clearing_doctypes`. 6-field cron (`hooks.py:340,349` `0/5`, `0/30`) supported via `scheduler_tick_interval` + croniter. ListPage/PrintPage order swapped in v16 renderers list — no impact on custom `metrics` renderer.
- T8 — frontend pin. DONE 2026-09-28 (reviewed, no pin change). Dashboard is decoupled Vue SPA (`dashboard/package.json:33` `frappe-ui 0.1.277`, Vue `^3.5.15`, `vite 8.0.1`); framework v16 uses esbuild + Vue `^3.3.0`, no shared vite pipeline. Pins are recent. Accept deferred to Phase 4: run `cd dashboard && yarn build` smoke on v16 bench.
- T9 — pins/defaults cleanup. PARTIAL DONE 2026-09-28. Fixed: `name desc` -> `number desc` (`api/site.py:1821`, `site.py:404,410`, `marketplace.py:400`); `DEFAULT_DEPENDENCIES` bench `5.25.1` -> `5.31.0` (`frappe_version.py:15`); added V16 rows to `bench_dependency.json` (PY 3.14, Node 24.12.0, NVM 0.39.1, PIP 25.3/25.2, WKHTML 0.12.5/0.12.6; BENCH already had V16). JSON OK, py_compile OK. Left as documented decisions (no change): `Nightly number: 15` duplication, `bump_v16 enabled=1` asymmetry + missing V16 test, `default=1` stays V15 until tenant bake-in.

Order: T1/T2/T5 gate upgrade. T6a/T6b/T7a/T7b/T8 parallel during testing. T9 before default flip. T4 anytime. Nothing deferred.

## References

- Frappe wiki: `Migrating-to-version-16`, query-builder-migration.
- Tags: `v16.35.0` stable, `develop` = `17.0.0-dev`.
- Prior audit: subagent reports 2026-09-28 (has_permission, sort order, pins).
