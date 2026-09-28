# Copyright (c) 2020, Frappe and Contributors
# See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase

# Versions from here up are the ones an operator can pick in the dashboard, so
# they are the ones whose dependency editor has to offer something.
FIRST_PICKABLE_VERSION_NUMBER = 16


class TestFrappeVersion(FrappeTestCase):
	def test_create_frappe_version_with_default_dependencies(self):
		number = 99  # version with no fixtures
		frappe_version = frappe.get_doc(
			{
				"doctype": "Frappe Version",
				"name": f"Version {number}",
				"number": number,
			}
		).insert()
		self.assertEqual(len(frappe_version.dependencies), 5)

	def test_every_pickable_version_offers_its_dependencies_in_the_editor(self):
		"""A pickable version with no `Bench Dependency Version` rows gets an empty dropdown.

		The group takes its versions from `Frappe Version.dependencies`, while the
		dependency editor lists its options from `Bench Dependency Version` filtered
		on `supported_frappe_version`. Version 17 was added without the second set,
		so the editor had nothing to show for any V17 group.
		"""
		pickable = frappe.get_all(
			"Frappe Version",
			filters={
				"public": 1,
				"status": ("!=", "End of Life"),
				"number": (">=", FIRST_PICKABLE_VERSION_NUMBER),
			},
			fields=["name", "number"],
			order_by="number asc",
		)

		self.assertTrue(pickable, "no pickable Frappe Version found to check")

		without_options = []
		for version in pickable:
			document = frappe.get_doc("Frappe Version", version.name)
			for dependency in document.dependencies:
				rows = frappe.get_all(
					"Bench Dependency Version",
					filters={"parent": dependency.dependency, "supported_frappe_version": version.name},
					pluck="version",
				)
				if not rows:
					without_options.append(f"{version.name}/{dependency.dependency}")

		self.assertEqual(
			without_options,
			[],
			"these dependencies have no editor option for their Frappe Version",
		)
