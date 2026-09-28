import frappe
from frappe.utils import update_progress_bar


def execute():
	groups = frappe.get_all("Release Group", filters={"version": "Version 15"}, pluck="name")

	if not groups:
		return

	rows = frappe.get_all(
		"Release Group Dependency",
		filters={
			"parenttype": "Release Group",
			"parent": ["in", groups],
			"dependency": "BENCH_VERSION",
			"version": ["!=", "5.31.0"],
		},
		fields=["name", "parent"],
	)

	now = frappe.utils.now_datetime()
	for i, row in enumerate(rows):
		update_progress_bar("Bumping bench version on Version 15 groups", i, len(rows))
		# A group that already carries a 5.31.0 row must not gain a second one: duplicate
		# dependency keys make update_dependencies reject every future edit to the group.
		already_bumped = frappe.db.exists(
			"Release Group Dependency",
			{"parenttype": "Release Group", "parent": row.parent, "dependency": "BENCH_VERSION", "version": "5.31.0"},
		)
		if already_bumped:
			frappe.db.delete("Release Group Dependency", row.name)
			continue
		frappe.db.set_value("Release Group Dependency", row.name, "version", "5.31.0", update_modified=False)
		# Set what ReleaseGroup.on_update would have set. Saving each group instead would run every
		# Release Group validation during migrate, where one bad group aborts the whole patch.
		frappe.db.set_value("Release Group", row.parent, "last_dependency_update", now)

	frappe.db.commit()
