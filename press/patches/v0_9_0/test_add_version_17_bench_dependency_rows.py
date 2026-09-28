import frappe
from frappe.tests.utils import FrappeTestCase

from press.patches.v0_9_0.add_version_17_bench_dependency_rows import (
	FRAPPE_VERSION,
	VERSIONS_BY_DEPENDENCY,
	execute,
)


class TestAddVersion17BenchDependencyRows(FrappeTestCase):
	"""The dependency editor's dropdown was empty for every Version 17 group."""

	def setUp(self):
		super().setUp()
		self.clear_version_17_rows()

	def tearDown(self):
		self.clear_version_17_rows()
		frappe.db.rollback()

	def clear_version_17_rows(self):
		frappe.db.delete(
			"Bench Dependency Version",
			{"supported_frappe_version": FRAPPE_VERSION},
		)

	def picker_versions(self, dependency: str) -> list[str]:
		rows = frappe.get_all(
			"Bench Dependency Version",
			filters={"parent": dependency, "supported_frappe_version": FRAPPE_VERSION},
			pluck="version",
		)
		return sorted(rows)

	def test_patch_gives_every_dependency_a_version_17_option(self):
		execute()

		for dependency, versions in VERSIONS_BY_DEPENDENCY.items():
			self.assertEqual(
				self.picker_versions(dependency),
				sorted(versions),
				f"{dependency} has no Version 17 option for the dependency editor",
			)

	def test_patch_is_idempotent(self):
		execute()
		execute()

		self.assertEqual(self.picker_versions("WKHTMLTOPDF_VERSION"), ["0.12.5", "0.12.6"])

	def test_patch_completes_a_partially_populated_dependency(self):
		"""One hand-added row must not make the patch skip the rest."""
		frappe.get_doc("Bench Dependency", "WKHTMLTOPDF_VERSION").append(
			"supported_versions", {"version": "0.12.5", "supported_frappe_version": FRAPPE_VERSION}
		).save()

		execute()

		self.assertEqual(self.picker_versions("WKHTMLTOPDF_VERSION"), ["0.12.5", "0.12.6"])

	def test_patch_leaves_other_frappe_versions_alone(self):
		before = {
			dependency: sorted(
				frappe.get_all(
					"Bench Dependency Version",
					filters={"parent": dependency, "supported_frappe_version": "Version 16"},
					pluck="version",
				)
			)
			for dependency in VERSIONS_BY_DEPENDENCY
		}

		execute()

		for dependency, versions in before.items():
			self.assertEqual(
				sorted(
					frappe.get_all(
						"Bench Dependency Version",
						filters={"parent": dependency, "supported_frappe_version": "Version 16"},
						pluck="version",
					)
				),
				versions,
			)
