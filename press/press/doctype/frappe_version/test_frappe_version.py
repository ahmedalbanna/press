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
		"""A dependency the editor cannot offer is a dependency the operator cannot change.

		A Release Group takes its dependency versions from `Frappe Version.dependencies`,
		while the editor lists its choices from `Bench Dependency Version` filtered on
		`supported_frappe_version`. The dashboard injects the group's current value into the
		option list, so a dependency with no matching row does not look broken: it offers
		exactly one choice, the one already set, and the operator cannot move off it.

		Checked against the value a new group would actually get, not merely that some
		option exists. `NVM_VERSION` was the case in point -- offered only `0.39.1`, while
		every version defaults to `0.36.0`, which is a real nvm release that
		`press/docker/Dockerfile` installs.

		"Pickable" is `status != "End of Life"`, the filter `get_new_site_options` applies.
		An earlier version of this test used a version number instead, which silently
		skipped Nightly and Version 15 -- both offered, and both affected.

		Three queries, not one per (version, dependency) pair: the pair count grows with
		every version that gets offered.

		Reads the database, so it needs the site's fixtures and patches to be current --
		`bench --site <site> migrate`. On a site that has not migrated yet, the rows it
		looks for are not there, which is the same signal a stale install gives.
		"""
		pickable = frappe.get_all(
			"Frappe Version",
			filters={"public": 1, "status": ("!=", "End of Life")},
			pluck="name",
			order_by="number asc",
		)
		self.assertTrue(pickable, "no pickable Frappe Version found to check")

		declared = frappe.get_all(
			"Frappe Version Dependency",
			filters={"parent": ("in", pickable)},
			fields=["parent", "dependency", "version"],
			limit_page_length=0,
		)
		offered = {
			f"{row.supported_frappe_version}/{row.parent}/{row.version}"
			for row in frappe.get_all(
				"Bench Dependency Version",
				filters={"supported_frappe_version": ("in", pickable)},
				fields=["parent", "supported_frappe_version", "version"],
				limit_page_length=0,
			)
		}

		not_offered = sorted(
			f"{row.parent}/{row.dependency} (group default {row.version})"
			for row in declared
			if f"{row.parent}/{row.dependency}/{row.version}" not in offered
		)

		self.assertEqual(
			not_offered,
			[],
			"a new group on these versions would get a dependency the editor cannot offer; "
			"if the site has not migrated since these were added, run "
			"`bench --site <site> migrate`",
		)
