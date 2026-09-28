# Workspace inventory, doctor and render

One place that records the ports, paths, service names and secret locations for this
development box, so that installing an app, site, bench or server does not mean
retyping a URL, key or port each time.

## Why this exists

The values were always in the right place — the problem is that each tool kept its
**own copy** with nothing reconciling them:

- the same agent token appears in the supervisor conf, the MCP config and the skill docs
- the port map is expressed three times: `common_site_config.json`, nginx upstreams, and prose
- a bench's identity (path, site, ports) is restated by every script that touches it

So a port or token change means editing N files by hand and hoping you found them all.

## Files

| File | Purpose |
|---|---|
| `press-workspace.json` | The inventory. Git-safe, **no secret values**. |
| `bin/press-workspace` | The tool. Stdlib only, so it needs no venv. |

## Commands

```bash
W=ops/workspace/bin/press-workspace

$W doctor                     # verify the box matches the inventory
$W render                     # check the files the inventory owns (exit 1 on drift)
$W render --apply             # write the drift away
$W render --emit              # print expected content for root-owned files
$W render --only control      # limit to one target
$W ports                      # port ranges + next free set for a tenant bench
$W ports --json               # the allocation as JSON, for a script to consume
$W agent                      # agent URL and auth, token NOT printed
$W agent --env                # ready-to-eval export block
$W agent --ping               # call the agent /ping using the inventory's URL + token
$W show                       # print the resolved inventory
$W check-secrets              # confirm secret values are populated
```

`doctor`, `render` (check) and `ports` exit non-zero on failure, so any of them can gate a
script.

## Not retyping URLs, keys or ports

These two are the ones that remove the daily friction:

```bash
# which ports are live, and what a new tenant would get
$W ports
#   webserver 8005  socketio 9003  redis_cache 13004  redis_queue 11004

# hand a script the agent URL, token and CA bundle without writing any of them down
eval "$($W agent --env)"
curl -H "Authorization: Bearer $PRESS_AGENT_TOKEN" "$PRESS_AGENT_URL/ping"
#   {"message":"pong"}
```

`agent --print-token` exists for scripts that need the value, and reading it goes through
the inventory rather than a hardcoded literal in whichever script happens to be running.

## What `doctor` checks

- **Services** — each is running, running as the expected user, and (if it has a port)
  something is listening. Patterns are bench-scoped, so a process from a different bench
  cannot be mistaken for this one's.
- **Bench port config** — `common_site_config.json` agrees with the inventory for every
  workspace.
- **Nginx wiring** — upstreams match the inventory's gunicorn and socketio ports, and
  something listens on the workspace webserver port.
- **Supervisor config** — the programs defined in each conf are an exact match for the
  inventory, with the conf each program belongs to resolved from the inventory rather
  than guessed.
- **Secrets** — each is populated **at its authoritative source**. Values are never
  printed and never copied into the inventory.

## What `render` owns

| Target | Managed content | Writable by `press`? |
|---|---|---|
| `common_site_config.json` (control, tenant) | `webserver_port`, `socketio_port`, `redis_cache`, `redis_queue` | **yes** — `--apply` writes it |
| nginx upstreams (press.localhost) | the `server 127.0.0.1:<port>` lines | **no** — root-owned, `--emit` only |

Only the listed keys are managed. Everything else in the file is left byte-identical, so
a render is a minimal diff rather than a reformat. The file is written with Frappe's own
shape (`indent=1`, `sort_keys`, no trailing newline) so a no-op render produces an empty
diff and running `--apply` twice changes nothing.

**The privilege boundary is deliberate.** Bench configs live under `/home/press` and are
writable. `/etc/nginx` and `/etc/supervisor` are root-owned, so `render` will not try to
write them and will not pretend to: it reports the drift, prints the expected block with
`--emit`, and names the `sudo nginx -t && systemctl reload nginx` that has to follow.
Rewriting those files without a config test would be worse than not automating them.

## Design rules

**The inventory never stores a secret value.** Each secret names where its value already
lives (`site_config.json`, the supervisor `environment=` line) and the tool reads that
place. Copying values in would create a second copy to keep in sync, which is the exact
problem this removes.

**Match patterns are bench-scoped.** A bare pattern like `worker --queue short,default`
also matches the *other* benches on this box, which silently produces a false "running".
Every pattern includes the bench path or the port.

**Service → supervisor program is explicit.** The program name alone is ambiguous:
`press-agent.conf` defines `[program:web]`, not `agent:web`, and `web` also appears in
other benches' confs. Each service records the conf it belongs to, and the name
supervisorctl uses, so the mapping is checked rather than guessed.

## Port allocation

A port is offered to a new tenant only if it is **neither listening on the box nor
already claimed** by a workspace, a service, or the `reserve` list. A bench that binds
either fails at supervisor start, long after the command that created it — so the check
has to happen before the bench exists.

Allocation reads **live sockets**, never process command lines. That is deliberate: a
process can name a port it failed to bind. On this box pids 3435/3436 claim
`0.0.0.0:13000` and `0.0.0.0:11000` in their command line while holding no socket at
all, and a cmdline scan would both report those as taken and miss the real listeners,
which are owned by `frappe` and therefore invisible to a per-user scan.

Adding the new tenant to the inventory's `workspaces` is what reserves its ports for the
next allocation.

## Agent runtime state lives in agent-data, not the agent's source tree

`/home/press/agent` is the agent's **git checkout** (`develop`, with a real local fix
to `agent/site.py` for S3 `endpoint_url` against MinIO). It is not a workspace, and
generated state does not belong in it. Three paths did:

| Path | Size | Why it landed there |
|---|---|---|
| `.docker-builds` | 333M | `agent/builder.py:934` — `os.getcwd()/".docker-builds"` |
| `.clones` | 281M | same cwd-relative pattern, clone cache |
| `appendonlydir` | 51M | `redis.conf` hardcodes `dir` |

**665M of build output, clone cache and redis AOF inside a source checkout.** The cost
was not tidiness: the agent dir had to stay `frappe`-writable to hold them, which is
exactly what the "never chown agent dirs to `press`" rule exists to prevent, and
`repo/` had ended up mode **777**.

They now live in `/home/press/agent-data/agent/`, with symlinks left in the checkout so
the agent needs **no source edit** and survives an agent upgrade. `redis.conf`'s `dir`
is absolute and does *not* follow a symlink, so it is configured explicitly.

`agent_data/agent/nginx` and `agent_data/agent/tls` already existed, so this makes the
box consistent rather than inventing a third convention — the agent already kept nginx
and TLS state there.

### Why not just patch the agent?

`agent/builder.py` and `agent/server.py` are cwd-relative **in the agent's own repo**
(`frappe/agent`, branch `develop`). Editing them here would be silently reverted by the
next `agent` upgrade, and would leave the box looking fixed when it is not. The symlink
is the one lever that changes behaviour without touching a file that gets overwritten.

### `doctor` guards this

```
ok    .docker-builds   in /home/press/agent-data/agent, symlinked from the checkout
ok    redis dir      dir /home/press/agent-data/agent
```

It **fails** if a runtime dir is a real directory in the checkout again (the state a
re-clone leaves behind) and **warns** if a symlink is missing (the agent will recreate
the dir in the source tree). Both modes are tested.

## Workspaces

Three, and they are easy to confuse — the first version of this inventory did:

| Workspace | What it is | Ports are |
|---|---|---|
| `control` | the Press control plane, bare metal, under `/home/press` | its own, 8003/8004/9002/13002/11002 |
| `tenant` | **the live tenant, a container** (`bench-0001-000014-apps0`) | *host-published*: 18003/19003/13003/11003 |
| `test_bench` | a separate bare-metal bench for trying things out | 8000/9000/13000/11000 |

Tenant paths are **not ours to rename**. The agent derives them:

```python
# agent/cli.py:81
"benches_directory": f"/home/{user}/benches"
```

and the running agent's `config.json` agrees: `benches_directory: /home/press/benches`.
Press and the agent share that path, and each tenant dir is named after its Bench record,
so `bench-0001-000014-apps0` is the Bench's name, not an accident of layout. What was
missing was legibility, so the inventory maps the opaque name to its site, ports and
container — `doctor` resolves it.

`/home/press/benches/bench-0001-000014-apps0/` on the host is the tenant container's
**bind mount**, not a bench. The container's own bench listens on 8000/9000/11000/13000
*inside* the container; docker publishes them elsewhere. Anything host-side — an nginx
upstream, a curl, a port check — must use the published numbers, so those are what the
inventory records.

`test_bench` is not containerised, which is also why it still shows 8000/9000 as live:
those ports belong to it on the host. The real tenant's dirs are `frappe:frappe 2775` and
must never be chowned to `press`, so the container's `common_site_config.json`
(`frappe:frappe` mode **600**) is deliberately **not** a render target — this user cannot
read it. The inventory records that exclusion in
`render._common_site_config_excluded` so its absence is a decision on record rather than
an oversight.

## Port allocation

A port is offered to a new tenant only if it is **neither listening on the box nor
already claimed** by a workspace, a service, or the `reserve` list. A bench that binds
either fails at supervisor start, long after the command that created it — so the check
has to happen before the bench exists.

Allocation reads **live sockets**, never process command lines. That is deliberate: a
process can name a port it failed to bind. On this box pids 3435/3436 claim
`0.0.0.0:13000` and `0.0.0.0:11000` in their command line while holding no socket at
all, and a cmdline scan would both report those as taken and miss the real listeners,
which are owned by `frappe` and therefore invisible to a per-user scan.

## new-tenant is a pre-flight, not a second provisioning path

`new-tenant --site <name>` checks what can be checked without the control plane — the
name, port availability, and that the agent answers — and then prints the provisioning
chain with everything filled in. **It provisions nothing.**

That is on purpose. On this box provisioning belongs to press-mcp:
`check_site_placement` → `production_readiness_audit` → `build_release_group` →
`deploy_build` → `create_site`, with the `retry_*` tools for the known failure modes.
Re-typing that as raw `bench` commands would create a parallel path that drifts from the
supported one and would get the ownership rules wrong — tenant bench dirs stay
`frappe:frappe` and must never be chowned to `press`. The pre-flight also names the three
settings that otherwise fail *late*, after a fifteen-minute build:
`set_press_setting` (domain + registry URL + `no_push`), `set_docker_registry_credentials`
(the agent always runs `docker login`, and docker refuses an empty username), and
`set_bench_port_offset` if a bench reports `address already in use` — because
`get_unused_port_offset` is blind to this machine.

## Still to come

Done: the inventory, `doctor`, `render` for the files `press` owns, `ports`, `agent`,
`new-tenant`.

1. bringing nginx and supervisor under management via a sudo wrapper that runs
   `nginx -t` before reloading
2. `doctor` becomes the regression check for that
3. optionally: a `readiness` alias that chains `doctor` + `render` for a single
   go/no-go before touching the control plane

## Known oddity on this box, not yet addressed

Two redis processes (pids 3435/3436, owner `frappe`) advertise `0.0.0.0:13000` and
`0.0.0.0:11000` but hold no listening socket — the real listeners on those ports are
`127.0.0.1:13000`/`127.0.0.1:11000` (pids 820/821). They are leftovers from a previous
configuration. `doctor` does not flag them because they hold nothing, and killing them
is a judgement call about which bench they belong to rather than something to automate.

## Caveats

- `supervisorctl` is unusable as the `press` user: the socket is root-owned `srwx------`.
  The tool therefore inspects config files and processes directly rather than asking
  supervisor for status. It reads the confs, which are world-readable.
- The control bench gunicorn runs with `--preload`, so `kill -HUP` does **not** pick up
  code changes. Use `sudo supervisorctl restart press-bench-web`.
