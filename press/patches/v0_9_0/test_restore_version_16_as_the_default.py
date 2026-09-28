import frappe
from frappe.tests.utils import FrappeTestCase

from press.patches.v0_9_0.restore_version_16_as_the_default import DEFAULT_VERSION, execute


class TestRestoreVersion16AsTheDefault(FrappeTestCase):
	"""The flip to Version 17 was reverted; sites that ran it need this to converge."""

	def setUp(self):
		super().setUp()
		self.original = {
			row.name: row.default
			for row in frappe.get_all("Frappe Version", fields=["name", "default"], limit_page_length=0)
		}

	def tearDown(self):
		for name, was_default in self.original.items():
			frappe.db.set_value("Frappe Version", name, "default", was_default, update_modified=False)
		frappe.db.rollback()

	def defaults(self) -> list[str]:
		return frappe.get_all("Frappe Version", filters={"default": 1}, pluck="name", limit_page_length=0)

	def test_clears_a_default_set_on_another_version(self):
		"""The state a site that already ran the flip is in."""
		frappe.db.set_value("Frappe Version", "Version 17", "default", 1, update_modified=False)
		frappe.db.set_value("Frappe Version", DEFAULT_VERSION, "default", 0, update_modified=False)

		execute()

		self.assertEqual(self.defaults(), [DEFAULT_VERSION])

	def test_sets_the_default_when_none_is_set(self):
		for name in self.defaults():
			frappe.db.set_value("Frappe Version", name, "default", 0, update_modified=False)

		execute()

		self.assertEqual(self.defaults(), [DEFAULT_VERSION])

	def test_patch_is_idempotent(self):
		execute()
		execute()

		self.assertEqual(self.defaults(), [DEFAULT_VERSION])

	def test_patch_leaves_status_alone(self):
		"""`status` is what the upgrade target resolves on, and is a separate decision."""
		frappe.db.set_value("Frappe Version", "Version 17", "default", 1, update_modified=False)
		before = frappe.db.get_value("Frappe Version", "Version 17", "status")

		execute()

		self.assertEqual(frappe.db.get_value("Frappe Version", "Version 17", "status"), before)
