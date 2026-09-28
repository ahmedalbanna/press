"""Make every pickable Frappe Version's dependency defaults selectable in the editor.

A Release Group takes its dependency versions from `Frappe Version.dependencies`, but the
dependency editor lists its choices from `Bench Dependency.supported_versions` filtered on
`supported_frappe_version`. Where the two disagree, the editor shows the group's current
value and nothing else -- the dashboard injects `dependency.version` into the option list --
so the operator cannot move off it, and cannot reach any other version on offer.

This reads the defaults out of `Frappe Version.dependencies` and adds whatever the editor is
missing, so it holds for every pickable version rather than for one hand-picked list. It is
the safety net behind `test_every_pickable_version_offers_its_dependencies_in_the_editor`,
which fails the moment a version lands with a dependency the editor cannot offer.

It only ever *adds* options. The version a new group builds with comes from
`Frappe Version.dependencies` and is deliberately left alone: correcting that instead would
change what every new group builds with, which is a decision for an operator, not a patch.

End-of-Life versions are skipped, matching what `get_new_site_options` will offer.
"""

import frappe


def pickable_versions() -> list[str]:
	return frappe.get_all(
		"Frappe Version",
		filters={"public": 1, "status": ("!=", "End of Life")},
		pluck="name",
		order_by="number asc",
	)


def missing_options() -> list[tuple[str, str, str]]:
	"""`(bench_dependency, frappe_version, version)` triples the editor cannot offer."""
	missing = []
	for version in pickable_versions():
		for dependency in frappe.get_all(
			"Frappe Version Dependency",
			filters={"parent": version},
			fields=["dependency", "version"],
			limit_page_length=0,
		):
			if not frappe.db.exists("Bench Dependency", dependency.dependency):
				continue

			offered = frappe.get_all(
				"Bench Dependency Version",
				filters={
					"parent": dependency.dependency,
					"supported_frappe_version": version,
				},
				pluck="version",
				limit_page_length=0,
			)
			if dependency.version not in offered:
				missing.append((dependency.dependency, version, dependency.version))

	return missing


def execute():
	# Grouped so each Bench Dependency is saved once, not once per missing option.
	by_dependency: dict[str, list[tuple[str, str]]] = {}
	for dependency, version, value in missing_options():
		by_dependency.setdefault(dependency, []).append((version, value))

	added = 0
	for dependency, rows in by_dependency.items():
		document = frappe.get_doc("Bench Dependency", dependency)
		for version, value in rows:
			document.append(
				"supported_versions",
				{"version": value, "supported_frappe_version": version},
			)
			added += 1
		document.save()

	print(f"Added {added} bench dependency options")
