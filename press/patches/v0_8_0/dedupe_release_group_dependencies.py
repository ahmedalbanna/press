"""Collapse duplicate Release Group Dependency rows.

A Release Group should carry exactly one row per dependency, but the
`bump_v*_bench_version_to_5_31_0` patches appended 5.31.0 to groups that
already had a row, so a group could end up with two rows for the same
dependency. That is not cosmetic: `press.api.bench.update_dependencies`
matches the submitted list against the group's rows positionally and raises
"Invalid dependency" as soon as a key appears twice, which locks the group
out of dependency editing entirely.

Both bump patches now delete the stale row instead of adding a second one;
this patch cleans up whatever they already left behind. The highest version
per dependency wins, which is the one a bump is trying to reach anyway.
"""

import frappe
from frappe.utils import update_progress_bar


def version_key(version: str) -> tuple[int, ...]:
	"""Sortable key for a dotted version.

	Only the leading digits of each component count, so a pre-release suffix
	does not inflate it: `5.31.0-rc1` sorts the same as `5.31.0`, not above it.
	"""
	key = []
	for chunk in str(version).split("."):
		digits = ""
		for char in chunk:
			if not char.isdigit():
				break
			digits += char
		key.append(int(digits) if digits else 0)
	return tuple(key)


def execute():
	groups = frappe.get_all("Release Group", pluck="name")
	if not groups:
		return

	rows = frappe.get_all(
		"Release Group Dependency",
		filters={"parenttype": "Release Group", "parent": ["in", groups]},
		fields=["name", "parent", "dependency", "version"],
	)

	by_dependency: dict[tuple[str, str], list] = {}
	for row in rows:
		by_dependency.setdefault((row.parent, row.dependency), []).append(row)

	duplicates = {key: group_rows for key, group_rows in by_dependency.items() if len(group_rows) > 1}
	if not duplicates:
		return

	for i, ((parent, dependency), group_rows) in enumerate(duplicates.items()):
		update_progress_bar("Removing duplicate release group dependencies", i, len(duplicates))
		keep = max(group_rows, key=lambda row: version_key(row.version))
		for row in group_rows:
			if row.name != keep.name:
				frappe.db.delete("Release Group Dependency", row.name)

	frappe.db.commit()
