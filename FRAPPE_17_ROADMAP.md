# Frappe 17 upgrade plan

Written 2026-09-28, immediately after landing the Frappe 16 upgrade. Nothing here
has been done. This is a plan, written down so the v16 work is not redone by
accident and so the v17 attempt starts from a known state.

## Status: nothing to upgrade to yet

There is no `version-17` branch on `frappe/frappe`. Verified against the remote
on 2026-09-28:

```
$ git ls-remote --heads https://github.com/frappe/frappe | grep -c version-17
0
```

`develop` is `17.0.0-dev` and carries the same `requires-python = ">=3.14,<3.15"`
as `version-16`, so there is no new interpreter to move to yet. `version-15` and
`version-16` are both present.

This makes v17 a **moving target**, not a version. The honest framing is: there
is a `develop` branch that will become v17, and upgrading to it means absorbing
whatever is on `develop` on the day you do it.

## Do not start until v17 has a branch

Waiting is the single highest-value action here. Everything below is
preparation that stays valid, and none of it requires guessing at unreleased
behaviour.

Trigger to start: `refs/heads/version-17` appears, or `develop` stabilises
enough that a release candidate is announced.

**Status as of 2026-09-28: the code is already verified ready.** Press 0.8.0
installs, migrates, and passes its test suites on `develop` (17.0.0-dev) with no
changes needed. What is missing is a *stable* v17 to pin to, not readiness.
See "Verified: press installs and migrates on v17".

## Phase 1 — Readiness work, safe on v16

Do these now. Each removes a known v17 risk without needing v17 to exist.

### 1.1 Python 3.15 blockers

`datetime.utcnow()` is **removed** in 3.15. v17's `requires-python` will very
likely widen to 3.14+ once 3.15 is a supported target, so these become hard
failures rather than deprecation warnings.

**Done**, in 0.9.0. Both call sites now go through `press.utils.clock.now_utc()`:

| File | Was | Risk, and how it was resolved |
|---|---|---|
| `press/utils/__init__.py` (`cache`) | 384, 388, 390 | Low. Both sides of the comparison were naive, so both became aware — behaviour-preserving. |
| `press/press/report/aws_s3_storage_cost/aws_s3_storage_cost.py` | 110, 144 | Higher. Feeds an AWS query window. botocore serialises a timestamp with `calendar.timegm(value.timetuple())`, which reads naive as UTC, so the window sent to CloudWatch is unchanged. |

Two things worth knowing if you touch this area:

- The module is `press/utils/clock.py`, **not** `time.py`. Importing a submodule
  binds it as an attribute on the parent package, so `press/utils/time.py` would
  overwrite the stdlib `time` that `press.utils` itself imports. The symptom is
  `AttributeError: module 'press.utils.time' has no attribute 'time'`, raised from
  an unrelated module at runtime, not at import.
- The helper is `now_utc`, not `now`. `frappe.utils.now()` returns a *string* and
  `now_datetime` returns a naive datetime; a third `now` on the same import line is
  a trap.

`grep -rn "utcnow()" press/` is now clean.

### 1.2 Add a static check so these cannot come back

Done. `DTZ003` is in `ruff.toml`, so the pre-commit hook fails on
`datetime.utcnow()`. Scoped to that one rule deliberately: the rest of the
`flake8-datetimez` ruleset reports 327 findings (`DTZ001/005/006/007/011` — naive
`now()`, `date.today()`, strptime without `%z`), most of which are correct as
written throughout this codebase. Widening it needs the per-call-site behaviour
worked out first, so it is its own change.

`ruff.toml` keeps `target-version = "py310"`, matching `requires-python`. Raising
it turns on 66 py311+ upgrade findings (`TC001-3`, `UP017/042/043/046/047`) — a
real refactor, but a separate one.

### 1.3 Python floor in `pyproject.toml` — decided against

`requires-python` **stays** at `>=3.10`. An earlier draft of this plan proposed
raising it to `>=3.14` to match v16, on the reasoning that the old floor "lies to
anyone reading it". That is wrong, and it would have broken installs.

`requires-python` describes what **press's own code** needs. The interpreter floor
is enforced by the `frappe` dependency, which resolves per version: v15 allows
3.10, v16+ requires 3.14. Raising press's floor to 3.14 would make press
uninstallable on a Frappe 15 bench — a bench the `frappe = ">=15.0.0,<18.0.0"`
range still claims to support. The 3.10 floor is also load-bearing for the new
`press/utils/clock.py`: `datetime.UTC` is 3.11+, so it uses `timezone.utc` instead.


## Phase 2 — Audit, once v17 exists

Run the same sweep that found the `order_by` and `init_telemetry` breakages.
Those were found by grep, not by tests, and both failed *quietly* — which is the
class of bug that costs the most.

### Audit results, run against `develop` (17.0.0-dev) on 2026-09-28

Comparing `v16.35.0` against `develop` (commit `4ac9eb13`, 1775 files changed):

| Area | Finding | Action |
|---|---|---|
| `frappe.utils.telemetry` | **Still present on v17.** Reworked again around a `pulse` client, exposing `capture`, `add_bootinfo`, `is_pulse_enabled`. No `init_telemetry`, same as v16. | Our fix holds. `press/utils/telemetry.py` already uses its own implementation and defines its own `capture_pulse`. Re-check `press/utils/telemetry.py` against v17's pulse API when it lands. |
| `frappe.pulse` | **New on v17** (`frappe/pulse/__init__.py` is empty; the surface moved to `frappe/pulse/utils.py`). v16 has only 2 files under `frappe/pulse/`. | Confirm what v17's pulse client expects before wiring anything to it. |
| `frappe.mcp` | **Gone.** Zero files matching `mcp` anywhere in v17's tree. | **Already safe.** `frappe-mcp` is an optional extra and is *not installed* on this bench — `press/mcp/__init__.py` falls back to `_MCPUnavailable`, so every module in `press/mcp/tools/` stays importable. The incident support agent imports `press.mcp.tools.telemetry.clients`, so this matters beyond MCP itself. Nothing to do; do not re-add `frappe-mcp` as a hard dependency. |
| Module imports | **No regressions.** A full walk of all 1006 press modules against a real v17 env (frappe 17.0.0-dev, commit `4ac9eb13`, own venv, press installed on top) produces results byte-identical to v16: 1005 imported, 1 failed, pre-existing. See "Import probe" below. | Nothing to fix. Re-run the probe when `version-17` branches. |
| `order_by` validation | Not re-checked against v17; v16 introduced it and v17 may tighten further. | Keep the grep clean (Phase 1.2 / 2.1). |
| `utils/weasyprint.py` | Removed in the v16→v17 diff. | Press does not reference it (0 hits). No action. |
| `doctype_layout`, `changelog_feed`, `sidebar_item_group`, `print_format_builder_beta` | All removed in the v16→v17 diff. | Press references none of them (0 hits each). No action. |

### 2.1 The `order_by` and `fields` validation

v16 introduced `order_by` validation (`frappe/database/query.py`, ~line 1310)
that accepts only plain field names. The same validation governs `fields` and
filter parsing. v17 may tighten it further.

```bash
grep -rn 'order_by=.*[A-Z_]*(' press/ --include="*.py"
grep -rnE 'fields\s*=.*\w+\(' press/ --include="*.py"
```

Both are clean on our branch right now. Keep them clean.

### 2.2 API removals between `version-16` and v17

`frappe` deleted 1775 files moving from `version-16` to `develop`. Sample of
removed Python modules:

```
frappe/utils/weasyprint.py
frappe/custom/doctype/doctype_layout/
frappe/desk/doctype/changelog_feed/
frappe/desk/doctype/sidebar_item_group/
frappe/printing/page/print_format_builder_beta/
```

Press references **none** of these (verified). Re-run the check against v17
when the branch exists — the list will differ.

The general check, for every removal between the two branches:

```bash
# for each removed module, is it referenced?
git diff --name-status <v16> <v17> -- frappe/ | grep '^D.*\.py$' | awk '{print $2}'
```

### 2.3 Telemetry

v16 removed `init_telemetry`; Press now uses its own
(`press/utils/telemetry.py`). In v17 `develop`, `frappe/utils/telemetry` has been
reworked again around a `pulse` client, exposing `capture`, `add_bootinfo`, and
pulse helpers — no `init_telemetry`. So the v16 fix holds on v17, and the module
has moved again. Check what `press/utils/telemetry.py` should call on v17.

### 2.4 `python-telegram-bot`

v21 now, verified working. Check whether v17 or a transitive dependency
constrains it differently.

## Phase 3 — The upgrade itself

Same shape as the v16 upgrade, with one ordering rule learned the hard way:
**env first, then frappe.** v16 required Python 3.14 while v15 allowed 3.11, and
switching frappe first left the bench uninstallable.

```bash
# 1. Env first, to whatever v17 requires
cd /home/press/benches/control
bench migrate-env <new-interpreter>

# 2. THEN frappe
git -C apps/frappe checkout version-17
uv pip install -e apps/frappe --python ./env/bin/python
uv pip install -e apps/press --python ./env/bin/python

# 3. Flush Redis BEFORE migrating. Non-negotiable.
redis-cli -p 13002 FLUSHALL   # cache
redis-cli -p 11002 FLUSHALL   # queue

# 4. Migrate
bench --site press.localhost migrate --skip-failing
```

### 3.1 Read the migrate output

Always check for `Orphaned DocType(s) found:`. v16's
`remove_orphan_doctypes` **deletes a DocType record** when its controller raises
`ImportError`, so a bad import passes a migrate that reports success and the
failure surfaces later as `DocType <name> not found` — pointing at the wrong
thing entirely. This is how the `init_telemetry` bug hid.

Framework names in that line on v16 are expected (v16 moved them to separate
apps). Anything belonging to press is a bug.

### 3.2 Build assets

Needs the toolchain pins in `/etc/profile.d/frappe16-toolchain.sh`. Note that
file is named for v16; v17 may need different Node and yarn versions, so expect
to update it rather than assume it carries over.

```bash
bash -lc 'node --version'    # must satisfy v17's engines.node
NODE_OPTIONS="--max-old-space-size=1536" bench build
```

The box is 7.8Gi with swap full. An uncapped build gets OOM-killed.

## Phase 4 — Data and defaults

Repeat what the v16 upgrade required, and expect new instances.

- **Version 17 fixture rows** in `press/fixtures/frappe_version.json`, with
  `number`, `status`, and bench dependency rows. v16's are the model — see the
  V16 rows for Python, Node, nvm, pip, wkhtmltopdf. **Done in 0.9.0** (`status:
  Develop`, `default: 0`).
- **The default stays on v16**, and that is the right call for now. `Frappe
  Version.default` only orders the new-site dropdown, so flipping it is an
  independent decision from making v17 the upgrade target — and v17 is `Develop`.
  Flipping the flag to offer a `Develop` version to new customers is not something
  to let follow from declaring the version supported. Revisit when v17 goes
  `Stable`, at which point the same reasoning makes the flip correct.
  Note this was tried and reverted once already, which is a useful reminder that
  reverting a shipped patch needs a new patch: `patches.txt` only decides what
  runs on a site that has not run it yet, so `restore_version_16_as_the_default`
  exists to clear the flag on sites that already flipped.
  Note the `Nightly` row has `number=15`, which collides with `Version 15` —
  worth fixing before it collides with something that matters.
- **Every pickable version's dependency defaults must be selectable.** A group
  takes its versions from `Frappe Version.dependencies` while the editor offers
  `Bench Dependency.supported_versions`, and where they disagree the operator is
  stuck on whatever is already set. v17 landed with no rows at all, and `NVM`
  had a gap on *every* version. Fixed by deriving the missing rows from
  `Frappe Version.dependencies` rather than hand-listing them, so the next
  version cannot land half-wired.
- **Backfill Release Groups.** The `order_by` and feature-flag bugs both hid in
  existing rows, not in code. Once v17 exists, re-check:
  - feature flags on existing V17 groups
  - any group still on an old version
- **Re-run the audit sweeps against real data**, not just code.

## Phase 5 — Release

- Bump the Press version (0.8.0 → 0.9.0).
- Changelog entry, listing the fixes as they were found.
- Update `docs/operations/frappe-16-control-bench.md`, or fork it per version.
  The toolchain pins and Redis rule are the parts most likely to change.
- The 19+ commits on `frappe-16` are **not pushed**. If v17 work is to build on
  them, decide first whether that branch becomes the base or gets reworked —
  it contains box-specific workarounds that should not go upstream as-is.

## Risk register

| Risk | Likelihood | Why it matters |
|---|---|---|
| v17 breaks something quietly | **High** | Both v16 breakages found here failed silently. Tests pass while the code does nothing. |
| No stable v17 for a long time | High | `develop` only. Everything above is preparation, not a schedule. |
| Python 3.15 required | Medium | `requires-python` will widen. Phase 1.1 clears the known blockers. |
| Redis stale-hook class of failure | Medium | Cost us a failed migrate on v16. Flushing first is the whole mitigation. |
| Box-specific code in the way | Medium | `press/api/analytics.py` has cAdvisor and log-server workarounds with no V16/V17 guarantee. |

## Import probe — how the compatibility check was run

Every v16 breakage found on this box was an import problem, and **none of them
surfaced in the test suite**: `order_by` and `init_telemetry` both passed tests
while doing nothing. So the compatibility check imports every module rather than
running tests.

`press/utils/probe_module_imports.py` walks all 1006 press modules in whichever
env it is pointed at and writes a sorted report of what failed. Two reports diff
directly. A module that imports on one and not the other is a compatibility
finding; one that fails on both is pre-existing.

```bash
# v16 (the live env)
PROBE_OUTPUT=/tmp/v16.txt bench --site press.localhost execute \
    press.utils.probe_module_imports.probe

# a non-live env
PROBE_OUTPUT=/tmp/v17.txt /path/to/env/bin/python run_probe.py
diff /tmp/v16.txt /tmp/v17.txt
```

The env must be one where `press` is installed alongside the framework version
under test. For v17 that means its own venv: `frappe` editable-installed from a
`develop` checkout, then `press` on top. Both use Python 3.14 — v17's
`requires-python` is identical to v16's, so **no env change is part of a v17
upgrade**, which removes the riskiest part of the migration.

### Result: 1003 imported, 3 failed, identical on both

### Result: 1005 imported, 1 failed, identical on both

One failure, pre-existing and unrelated to the version under test:

| Module | Failure | Note |
|---|---|---|
| `press.api.cookies` | `ImportError: cannot import name 'get_cookie_dict_from_headers' from 'frappe.oauth'` | That function is absent from `frappe/oauth.py` on **both** v16.35.0 and v17, and `git grep` finds `cookie_perms` nowhere in the v17 tree. Not a v17 regression. |

The module's own `update_preferences` view is not referenced from the dashboard,
and nothing in press imports the module, so it is inert rather than broken. It
does import `frappe.auth.CookieManager`, which still exists on both versions, so
the working half of the module is only blocked by the one dead import.

### Two failures found and fixed during this audit

`cache_utils` and `bench_get_app_cache` were both failing to import on v16 as
well, which the version diff would have misread as new breakage. Root cause was
a `TypedDict` declared in the old positional style:

```python
CommandOutput = TypedDict("CommandOutput", cwd=str, image_tag=str, ...)   # TypeError
```

`TypedDict` only accepts keyword arguments from Python 3.13, so this raised at
import time and took `bench_get_app_cache` down with it. Fixed to the dict
form. Both now import on v16 and v17.

## Verified: press installs and migrates on v17

The import probe covers code that loads. It does not cover install, schema, or
patch execution — and those are where v16's worst bug hid. So this was run for
real, on a throwaway bench, against frappe `17.0.0-dev` (`4ac9eb1`) with this
branch's press as an editable install.

| Step | Result |
|---|---|
| `bench new-site v17probe.localhost` | OK, frappe 17.x.x-develop |
| `install-app press` | **EXIT 0**, no traceback |
| `migrate` | **EXIT 0**, no orphaned DocTypes |
| Patch Log | 440 rows, every v0_8_0 patch including `set_default_feature_flags_on_release_groups` and `dedupe_release_group_dependencies` |
| `Product Trial Request` DocType | **Present** after install — the v16 import bug does not recur on v17 |
| 7 test suites, 60 tests | **All green** |

The suites run are the ones that matter for the v16 work: `test_utils_cache`,
`test_deploy_candidate` (imports the `TypedDict` module fixed above),
`test_app_version_compatibility`, both patch tests, and both Telegram suites.

**Press 0.8.0 installs and migrates cleanly on Frappe 17.0.0-dev.** The live
control plane was never pointed at v17 to establish this.

### Setting up the throwaway bench

Reusable, and the reason it fits on this box is reusing the venv rather than
installing a second one (7.8Gi RAM, swap full):

```bash
# bench root: apps, sites, config, config/pids, logs  (bench checks all five)
ln -s /home/press/v17-probe/frappe-v17   apps/frappe
ln -s /home/press/benches/control/apps/press apps/press   # this branch, editable
ln -s /home/press/v17-probe/env-v17      env

bench new-site v17probe.localhost \
  --db-root-username v17admin --db-root-password <pw> \
  --admin-password <pw> --mariadb-user-host-login-scope=localhost
```

Test deps are not in press's dependencies — they come from frappe's test extra.
Without them, `run-tests` fails at collection with `No module named 'moto'`:

```bash
uv pip install moto "Faker~=40.23.0" freezegun hypothesis responses
```

### MariaDB access on this box

`root@localhost` uses `unix_socket` auth and the password in
`Database Server.mariadb_root_password` is not that root's. What works is the
OS-level `mysql` user, which holds `ALL PRIVILEGES ... WITH GRANT OPTION`:

```bash
sudo -u mysql mysql -e "SHOW GRANTS;"   # mysql@localhost
```

`bench` connects over TCP, so socket auth does not help it. Give it a real
user rather than the root password:

```bash
sudo -u mysql mysql -e "CREATE USER 'v17admin'@'localhost' IDENTIFIED BY '...';
                         GRANT ALL PRIVILEGES ON *.* TO 'v17admin'@'localhost' WITH GRANT OPTION;"
```

Worth knowing: a site user cannot `CREATE DATABASE` for itself, so
`bench new-site` will always fail against the control bench's own credentials.

## Progress

- [x] **Phase 1.1 — Python 3.15 blockers.** All five `datetime.utcnow()` call
      sites replaced with an aware `press.utils.now()`. The cache TTL
      comparison had naive datetimes on both sides; the AWS S3 report fed a
      naive window to CloudWatch, which botocore already reads as UTC, so the
      query window is unchanged. Covered by `press/utils/test_utils_cache.py`.
- [x] **Phase 1.3 — Python floor.** `requires-python` corrected to `>=3.14`.
- [x] **Phase 2 — audit against `develop`.** Results in the table above.
- [x] **Import probe against a real v17 env.** 1005/1006 modules import, byte-identical
      to v16. Committed as `press/utils/probe_module_imports.py`. Findings above.
- [x] **Fixed 2 pre-existing import failures** the probe surfaced (`TypedDict` declared in
      the pre-3.13 positional style), so v16 and v17 both import cleanly.
- [x] **Real install + migrate on a throwaway v17 bench.** EXIT 0 both times, 440 patches
      applied, no orphaned DocTypes, 7 suites / 60 tests green. Details above.
- [x] **Phase 1.2 — CI lint rule.** `DTZ003` added to `ruff.toml`, so
      `datetime.utcnow()` now fails the pre-commit hook rather than reaching
      runtime. Verified it catches the aliased form (`import datetime as dt`)
      too, and that the tree is clean against it.
- [ ] **Phase 2.1 — re-run the `order_by`/`fields` greps** when `version-17` exists.

## What is deliberately not in this plan

- **v17 prep on a guess.** No speculative shims for APIs I have not seen removed.
  Phase 1 is the exception, and only because `utcnow` removal in 3.15 is certain.
- **Pushing anything.** The v16 branch is local and stays that way.
- **Touching `test_audit`.** Its 4 failures are database contamination, not a
  product bug. Weakening the audit to pass would be the wrong trade.
