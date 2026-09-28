"""Give Version 17 the bench dependency rows its dropdown needs.

A new Release Group gets its dependency versions from `Frappe Version.dependencies`,
but the dependency editor lists its options from `Bench Dependency Version` filtered
on `supported_frappe_version`. Adding the `Version 17` Frappe Version record without
matching `Bench Dependency Version` rows left the editor with an empty dropdown for
every V17 group.

Fixtures only reach new sites, so sites that already migrated need this. Values
mirror the Version 16 rows, which is what the V17 `Frappe Version` dependencies were
copied from.
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


def execute():
	if not frappe.db.exists("Frappe Version", FRAPPE_VERSION):
		return

	added = 0
	for dependency, versions in VERSIONS_BY_DEPENDENCY.items():
		if not frappe.db.exists("Bench Dependency", dependency):
			continue

		document = frappe.get_doc("Bench Dependency", dependency)
		already_present = any(
			row.supported_frappe_version == FRAPPE_VERSION for row in document.supported_versions
		)
		if already_present:
			continue

		for version in versions:
			document.append(
				"supported_versions", {"version": version, "supported_frappe_version": FRAPPE_VERSION}
			)
		document.save()
		added += len(versions)

	print(f"Added {added} {FRAPPE_VERSION} bench dependency rows")
