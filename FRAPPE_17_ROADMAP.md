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

## Phase 1 — Readiness work, safe on v16

Do these now. Each removes a known v17 risk without needing v17 to exist.

### 1.1 Python 3.15 blockers

`datetime.utcnow()` is **removed** in 3.15. v17's `requires-python` will very
likely widen to 3.14+ once 3.15 is a supported target, so these become hard
failures rather than deprecation warnings.

| File | Lines | Risk |
|---|---|---|
| `press/utils/__init__.py` | 384, 388, 390 | Low. Both sides of the comparison are naive, so converting both to aware `datetime.now(UTC)` is behaviour-preserving. |
| `press/press/report/aws_s3_storage_cost/aws_s3_storage_cost.py` | 110, 144 | Higher. Feeds an AWS query window. Read the surrounding code before changing; the fix is `datetime.now(UTC)` with a tz-aware formatter, and getting that wrong silently shifts the reporting window. |

Also worth a sweep: `grep -rn "utcnow()\|utcfromtimestamp\|datetime.utcnow" press/`.
Five is the current count, and it is low, which suggests the codebase is mostly
already clean.

### 1.2 Add a static check so these cannot come back

Done. `DTZ003` is in `ruff.toml`, so the pre-commit hook fails on
`datetime.utcnow()`. Scoped to that one rule deliberately: the rest of the
`flake8-datetimez` ruleset flags naive local times that are correct throughout
this codebase, and adopting it wholesale would bury the one rule that matters.

Note `ruff.toml` still says `target-version = "py310"` while
`requires-python` is now `>=3.14`. Raising it turns on 66 py311+ upgrade
findings (`TC001-3`, `UP017/042/043/046/047`) — a real refactor, but a separate
one. Left as its own change.

### 1.3 Widen the Python floor in `pyproject.toml`

Currently `requires-python = ">=3.10"`. That is already inaccurate: v16 requires
`>=3.14,<3.15`, so the declared floor lies to anyone reading it. Correct it to
match what v16 actually needs. Decide the ceiling separately, since it is a
statement about what Press supports rather than what Frappe requires.

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
  V16 rows for Python, Node, nvm, pip, wkhtmltopdf.
- **Decide the default.** v16 is currently `default=1`. When v17 ships, decide
  whether to flip. Note the `Nightly` row has `number=15`, which collides with
  `Version 15` — worth fixing before it collides with something that matters.
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

## Progress

- [x] **Phase 1.1 — Python 3.15 blockers.** All five `datetime.utcnow()` call
      sites replaced with an aware `press.utils.now()`. The cache TTL
      comparison had naive datetimes on both sides; the AWS S3 report fed a
      naive window to CloudWatch, which botocore already reads as UTC, so the
      query window is unchanged. Covered by `press/utils/test_utils_cache.py`.
- [x] **Phase 1.3 — Python floor.** `requires-python` corrected to `>=3.14`.
- [x] **Phase 2 — audit against `develop`.** Results in the table above.
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
