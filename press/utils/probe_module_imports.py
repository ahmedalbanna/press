"""Report which press modules import cleanly, and which fail and why.

Run against several environments and diff the results. A module that imports on one
and not another is a framework compatibility finding; one that fails on both is
pre-existing and unrelated to the version under test.

    PROBE_OUTPUT=/tmp/v16.txt bench --site press.localhost execute press.utils.probe_module_imports.probe
    PROBE_OUTPUT=/tmp/v17.txt bench --site press.localhost execute press.utils.probe_module_imports.probe
    diff /tmp/v16.txt /tmp/v17.txt

Works on any bound site; it hardcodes `press.localhost` for the site it connects as.

Set `PROBE_OUTPUT` to control the destination; the report is also printed to stdout
so it works without it. Output is sorted, so two runs of the same code diff clean.

Walks with a site connected and as Administrator: several press controllers read
settings or query tables at import time, so an unbound site produces
`RuntimeError: object is not bound` and reports breakage that is not real. The walk
is read-only apart from `frappe.db.rollback()`, so run it on a scratch site.
"""

import importlib
import os
import pkgutil

import frappe
import frappe.utils

OUTPUT = os.environ.get("PROBE_OUTPUT")

# Skipped because they are expected to be unavailable in a given environment rather
# than broken, and their absence is a supported state.
SKIP_SUBSTRINGS = (".mcp.", ".tests.")
SKIP_SUFFIXES = (".mcp",)


def iter_press_modules():
	"""Every press module worth importing, excluding tests and optional extras."""
	import press

	for module in pkgutil.walk_packages(press.__path__, "press."):
		if any(substring in module.name for substring in SKIP_SUBSTRINGS):
			continue
		if module.name.endswith(SKIP_SUFFIXES) or "test_" in module.name:
			continue
		yield module.name


def bind_site() -> None:
	"""Connect to the site the probe walks with.

	Frappe resolves the bench dir by walking up from cwd to find `sites`, then writes
	log files under <bench>/<site>/logs. A probe env has no site dir of its own and
	fails there before reaching any press code, which looks like a framework failure
	but is not one. Create the log dir for both the resolved bench dir and cwd, so
	the walk can land anywhere.
	"""
	for root in (frappe.utils.get_bench_path(), os.getcwd()):
		if root:
			os.makedirs(os.path.join(root, "press.localhost", "logs"), exist_ok=True)
	os.makedirs("press.localhost/logs", exist_ok=True)

	frappe.init(site="press.localhost", sites_path=os.environ.get("PROBE_SITES_PATH"))
	frappe.connect()
	frappe.set_user("Administrator")


def probe() -> None:
	"""Write the report to `PROBE_OUTPUT`, or stdout when that is unset."""
	bind_site()

	failures = []
	imported = 0
	modules = sorted(iter_press_modules())

	for name in modules:
		try:
			importlib.import_module(name)
			imported += 1
		except Exception as e:
			failures.append(f"FAIL {name} | {type(e).__name__} | {str(e).split(chr(10))[0][:100]}")

	frappe.db.rollback()

	lines = [f"RESULT imported={imported} failed={len(failures)} total={len(modules)}", *sorted(failures)]
	report = "\n".join(lines) + "\n"

	if OUTPUT:
		os.makedirs(os.path.dirname(os.path.abspath(OUTPUT)), exist_ok=True)
		with open(OUTPUT, "w") as f:
			f.write(report)
		print(f"PROBE wrote {OUTPUT}")
	else:
		print(report, end="")
