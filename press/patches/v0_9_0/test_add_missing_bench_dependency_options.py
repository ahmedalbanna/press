import frappe
from frappe.tests.utils import FrappeTestCase

from press.patches.v0_9_0.add_missing_bench_dependency_options import (
	execute,
	missing_options,
	pickable_versions,
)

NVM_V17 = {"parent": "NVM_VERSION", "supported_frappe_version": "Version 17"}


class TestAddMissingBenchDependencyOptions(FrappeTestCase):
	"""A dependency with no matching option row cannot be changed from the dashboard.

	Every test here arranges its own starting state rather than assuming one, because the
	rows this patch adds are only present on a site that has migrated.
	"""

	def tearDown(self):
		frappe.db.rollback()

	def offered(self, dependency: str, version: str) -> list[str]:
		return sorted(
			frappe.get_all(
				"Bench Dependency Version",
				filters={"parent": dependency, "supported_frappe_version": version},
				pluck="version",
			)
		)

	def remove_option(self, **filters):
		frappe.db.delete("Bench Dependency Version", filters)

	def test_patch_makes_every_pickable_version_offer_its_group_default(self):
		"""The invariant, asserted after the patch rather than before it."""
		execute()

		self.assertEqual(
			missing_options(),
			[],
			"a new group would still get a dependency the editor cannot offer",
		)

	def test_patch_adds_a_missing_option_without_removing_the_existing_one(self):
		"""0.36.0 is the declared default; 0.39.1 is what the editor already offered."""
		self.remove_option(version="0.36.0", **NVM_V17)
		self.assertNotIn("0.36.0", self.offered("NVM_VERSION", "Version 17"))

		execute()

		self.assertIn("0.36.0", self.offered("NVM_VERSION", "Version 17"))
		self.assertIn("0.39.1", self.offered("NVM_VERSION", "Version 17"))

	def test_patch_is_idempotent(self):
		execute()
		execute()

		self.assertEqual(self.offered("NVM_VERSION", "Version 17"), ["0.36.0", "0.39.1"])

	def test_patch_does_not_touch_end_of_life_versions(self):
		"""No new group is created for an EOL version, so its options are not extended."""
		before = self.offered("NVM_VERSION", "Version 13")
		self.assertNotIn("Version 13", pickable_versions())

		execute()

		self.assertEqual(self.offered("NVM_VERSION", "Version 13"), before)

	def test_missing_options_reports_a_gap_it_finds(self):
		"""Guards the guard: `missing_options` must be able to return something."""
		self.remove_option(version="0.36.0", **NVM_V17)

		self.assertIn(("NVM_VERSION", "Version 17", "0.36.0"), missing_options())
