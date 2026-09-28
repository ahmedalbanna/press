"""Backfill the rq/gunicorn feature flags on Release Groups created before they existed.

`ReleaseGroup.setup_default_feature_flags` runs from `before_insert`, so it only
ever set the flags on groups created after it landed. Every group created
earlier kept the DocType defaults of 0, and since the flags decide how benches
are built, a Version 16 group could end up built without `use_rq_workerpool` or
with a single gunicorn thread per worker.

Reported in frappe/press#4601.
"""

import frappe

from press.press.doctype.release_group.release_group import default_feature_flags


def execute():
	# Only groups with nothing set. A group that has any flag populated was
	# either configured deliberately or already handled, and overwriting an
	# operator's choice would be worse than leaving a default in place.
	groups = frappe.get_all(
		"Release Group",
		filters={
			"gunicorn_threads_per_worker": 0,
			"use_rq_workerpool": 0,
			"merge_default_and_short_rq_queues": 0,
		},
		fields=["name", "version"],
		limit_page_length=0,
	)

	if not groups:
		return

	# dict(rows) on a list of dicts would iterate each dict's keys instead of
	# building a mapping, and silently yield something useless. Index it properly.
	number_by_version = {
		row.name: row.number
		for row in frappe.get_all("Frappe Version", fields=["name", "number"], limit_page_length=0)
	}

	for group in groups:
		flags = default_feature_flags(
			group.version,
			number_by_version.get(group.version, 0),
		)
		if not flags:
			continue
		frappe.db.set_value("Release Group", group.name, flags)
		print(f"Set feature flags on Release Group {group.name}: {flags}")
