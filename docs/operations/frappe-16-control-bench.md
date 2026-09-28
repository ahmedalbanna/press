# Operating the control bench on Frappe 16

Written 2026-09-28 while moving `/home/press/benches/control` from Frappe 15 to
Frappe 16.35.0 on Python 3.14.3. Everything here is something that cost time to
discover, so it is recorded rather than remembered.

- Control bench: `/home/press/benches/control`, apps `frappe` + `press`
- Site used for verification: `press.localhost`
- Press version: 0.8.0 (branch `frappe-16`, local only, not pushed)
- Rollback: `git -C apps/frappe checkout version-15` (was `4fa1b14`), then
  `uv pip install -e apps/frappe --python ./env/bin/python`, then
  `bench migrate-env` back to a 3.11 interpreter

## Toolchain prerequisites

Frappe 16 tightened two things that this box did not have. Both are now installed
under the `press` user's home, and `/etc/profile.d/frappe16-toolchain.sh` puts them
on `PATH` for login shells.

| Tool | Version | Location | Why |
|---|---|---|---|
| Node | 24.12.0 | `~/.local/node24` | Frappe 16's `package.json` declares `engines.node >= 24`. The distro node in `/usr/local/bin` is 20.20.2 and `bench build` refuses to run. 24.12.0 matches the `Version 16` fixture pin. |
| yarn | 1.22.22 | `~/.local/bin` | Required by `bench build`. npm's global prefix is root-owned, so `npm install -g` fails with `EACCES`; a user prefix is used instead. |
| Rust | 1.98.1 | `~/.cargo` | Only needed to build sdists that have no wheel. See "Source builds" below. |
| community.mysql | 5.0.2 | `~/.ansible/collections` | ansible-core no longer bundles collections. Needed by the `install_tcmalloc_udf` and `mariadb_prepare_replica` roles. |

Check them with:

```bash
bash -lc 'node --version; yarn --version'
```

If `node --version` reports 20.x, the profile entry is not being read (a
non-interactive `bash -c` will not read it; use a login shell or source
`/etc/profile.d/frappe16-toolchain.sh`).

## Building frontend assets

```bash
cd /home/press/benches/control
yarn install --cwd apps/frappe   # only after switching the frappe branch
bash -lc 'bench build'
```

`bench build` is memory hungry. The box has 7.8Gi with swap already full, and an
unconstrained build was OOM-killed (exit 143). This succeeds:

```bash
NODE_OPTIONS="--max-old-space-size=1536" bench build
```

**Symptoms of a missing build:** pages render as HTML but the SPA never boots, and
the desk shows a "page not found" style error. Server-side routing is unaffected,
so `/desk` still 301s correctly to `/login` — the failure is purely the missing
bundles. Confirm with:

```bash
ls sites/assets/frappe/dist/js/ | head
curl -s -H "Host: press.localhost" http://127.0.0.1:8003/login \
  | grep -oE '/assets/frappe/dist/js/[^"]+' | head -3
```

## Upgrading the framework version

Order matters: **env first, then frappe.** Frappe 16 requires Python >= 3.14, so
switching frappe before the env leaves the bench uninstallable.

```bash
cd /home/press/benches/control
bench migrate-env /usr/local/bin/python3.14      # may fail on press; that is expected
uv pip install -e apps/press --python ./env/bin/python
git -C apps/frappe checkout v16.35.0
uv pip install -e apps/frappe --python ./env/bin/python
redis-cli -p <cache_port> FLUSHALL                # see below, this is not optional
redis-cli -p <queue_port> FLUSHALL
bench --site press.localhost migrate --skip-failing
supervisorctl restart press-bench-web: press-bench-workers: \
  press-bench-build-worker:press-bench-build-worker-0 press-bench-sync-worker
```

### Flush Redis before a major version migrate

The first v16 migrate failed with:

```
module 'frappe.cache_manager' has no attribute 'build_domain_restriced_doctype_cache'
```

Nothing was wrong with the code. v15 shipped that function with the typo
`restriced`; v16 renamed it to `restricted`. Press had the **v15 hook list cached
in Redis**, so `get_hooks("doc_events")` still resolved the old name.
`press.overrides.before_after_migrate` calls `frappe.cache.flushall()`, but only
in `after_migrate` — far too late.

Any major version switch can leave stale `app_hooks`, `doctypes` and friends
behind. Flush cache and queue first, every time.

### Read the "Orphaned DocType(s) found:" line

`frappe/model/sync.py:remove_orphan_doctypes` calls `get_controller()` for every
DocType and **deletes the DocType record** if the controller raises
`ImportError` or `DoesNotExistError`. A single bad import in an app therefore
silently removes that DocType from the site, and the next test run or deploy
fails with `DocType <name> not found` — pointing at the wrong thing entirely.

So after every migrate, check the migrate output for that line. The orphans
reported on a clean v16 run (`Newsletter`, `Blog Post`, `Energy Point*`,
`Dropbox Settings`, `Google Drive`, `Transaction Log`) are framework modules that
v16 genuinely extracted into separate apps, so their removal is expected. Anything
belonging to press is a bug — check that its controller imports.

```bash
grep -a "Orphaned DocType" /path/to/migrate.log
```

### Source builds need Rust

`uv pip install` falls back to building an sdist when no wheel matches the
interpreter, and some of those cannot be built without a Rust toolchain. The
press install on 3.14 needed it for `pydantic-core` (via `frappe-mcp`), which is
why `frappe-mcp` is now an optional extra rather than a hard dependency.

## Verifying a change

```bash
bench --site press.localhost migrate --skip-failing
bench --site press.localhost run-tests --app press --module <dotted.path>
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: press.localhost" http://127.0.0.1:8003/
```

Do not run two `run-tests` against the same site at once — they share test-record
state and one will die with `FileNotFoundError: .test_records.jsonl`.

Some suites cannot pass on this bench because its database is not empty.
`press.tests.test_audit` reads the whole `Site` table, so a real site such as
`store.butterfly-ye.store` counts as a site with no backup and the audit
correctly reports `Failure`. That is test isolation, not a product bug — do not
"fix" it by weakening the audit.

## Audit tooling is not installed in the control env

`semgrep` is an optional extra (`pip install -e .[audit]`) and is **deliberately not
installed here**. Press only ever invokes it as a CLI subprocess, and the marketplace
app audit resolves it in one of two ways:

1. `Marketplace Settings.audit_bench_path` -> `<bench>/env/bin/semgrep`
2. `shutil.which("semgrep")` on PATH

The audit runs as a background job in a worker, and the workers' PATH does not
include the bench `env/bin`:

```
$ tr '\0' '\n' < /proc/<worker pid>/environ | grep ^PATH
PATH=/home/press/.opencode/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:...
```

So an installed semgrep is unreachable by the only caller that needs it, while
still forcing `click`, `pyjwt` and `opentelemetry-api` to versions that conflict
with what Frappe pins. It was removed for that reason.

Until a dedicated audit bench exists, the marketplace app audit reports a
`semgrep_unavailable` result with remediation text. That is the honest state,
not a regression. To turn the checks on properly, stand up a separate bench with
semgrep installed and point `Marketplace Settings.audit_bench_path` at it — that
is what the setting exists for.

`opentelemetry-api` is kept even though it is only reachable via
`google-api-core`, which Frappe uses.

Verify the dependency tree is clean after any env change:

```bash
cd /home/press/benches/control && ./env/bin/pip check    # expect: No broken requirements found.
```

## Memory

7.8Gi total, swap routinely full. Workers have already been OOM-killed
(`Worker (pid:…) was sent SIGKILL! Perhaps out of memory?` in
`logs/web.error.log`). If builds or workers start failing mysteriously, check
`free -h` first.
