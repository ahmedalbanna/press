"""Put the default Frappe Version back on Version 16.

An earlier patch in this release set `Version 17` as the default, and that was reverted:
offering a `status: Develop` version first in the new-site dropdown should not follow from
merely declaring the version supported. `Frappe Version.default` only orders that dropdown,
so it is independent of the upgrade target, and the upgrade target is unaffected either way.

This exists as a patch rather than only as a fixture change because removing a patch from
`patches.txt` does not un-apply it. A site that already ran the flip keeps `Version 17`
flagged until something clears it, and the new-site dropdown would keep offering it.

Idempotent, and a no-op on a site that never had the flag on Version 17.
"""

import frappe

DEFAULT_VERSION = "Version 16"


def execute():
	if not frappe.db.exists("Frappe Version", DEFAULT_VERSION):
		return

	others = frappe.get_all(
		"Frappe Version",
		filters={"default": 1, "name": ("!=", DEFAULT_VERSION)},
		pluck="name",
		limit_page_length=0,
	)
	for name in others:
		frappe.db.set_value("Frappe Version", name, "default", 0, update_modified=False)
		print(f"Cleared default on Frappe Version {name}")

	frappe.db.set_value("Frappe Version", DEFAULT_VERSION, "default", 1, update_modified=False)
	print(f"{DEFAULT_VERSION} is the default Frappe Version")
