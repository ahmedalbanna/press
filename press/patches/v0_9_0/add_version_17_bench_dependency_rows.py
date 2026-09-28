"""Give Version 17 the bench dependency rows its dropdown needs.

A new Release Group takes its dependency versions from `Frappe Version.dependencies`,
but the dependency editor lists its options from `Bench Dependency Version` filtered on
`supported_frappe_version`. Adding the `Version 17` Frappe Version record without
matching rows left the editor with an empty dropdown for every V17 group.

Fixtures only reach new sites, so sites that already migrated need this. Values mirror
the Version 16 rows, which is what the V17 `Frappe Version` dependencies came from.
"""

import frappe

FRAPPE_VERSION = "Version 17"

VERSIONS_BY_DEPENDENCY = {
	"BENCH_VERSION": ["5.31.0"],
	"NODE_VERSION": ["24.12.0"],
	"NVM_VERSION": ["0.39.1"],
	"PIP_VERSION": ["25.2", "25.3"],
	"PYTHON_VERSION": ["3.14"],
	"WKHTMLTOPDF_VERSION": ["0.12.5", "0.12.6"],
}


def missing_versions(document, expected: list[str]) -> list[str]:
	"""`expected` versions this Bench Dependency does not yet offer for V17.

	Set difference rather than a presence check: a site that has one hand-added V17
	row still needs the rest, and a whole-dependency skip would leave that site
	broken exactly as before.
	"""
	present = {
		row.version for row in document.supported_versions if row.supported_frappe_version == FRAPPE_VERSION
	}
	return [version for version in expected if version not in present]


def execute():
	if not frappe.db.exists("Frappe Version", FRAPPE_VERSION):
		return

	added = 0
	for dependency, versions in VERSIONS_BY_DEPENDENCY.items():
		if not frappe.db.exists("Bench Dependency", dependency):
			continue

		document = frappe.get_doc("Bench Dependency", dependency)
		for version in missing_versions(document, versions):
			document.append(
				"supported_versions", {"version": version, "supported_frappe_version": FRAPPE_VERSION}
			)
			added += 1

		if document.has_value_changed("supported_versions"):
			document.save()

	print(f"Added {added} {FRAPPE_VERSION} bench dependency rows")
