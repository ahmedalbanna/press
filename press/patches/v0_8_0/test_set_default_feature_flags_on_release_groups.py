# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from press.patches.v0_8_0.set_default_feature_flags_on_release_groups import (
	execute,
)
from press.press.doctype.app.test_app import create_test_app
from press.press.doctype.release_group.release_group import default_feature_flags
from press.press.doctype.release_group.test_release_group import (
	create_test_release_group,
)

FLAG_FIELDS = (
	"gunicorn_threads_per_worker",
	"use_rq_workerpool",
	"merge_default_and_short_rq_queues",
)


class TestDefaultFeatureFlags(FrappeTestCase):
	"""The rq/gunicorn flags, and the backfill for groups that never got them.

	`setup_default_feature_flags` runs on insert, so a group created before it
	landed kept the DocType defaults of 0. frappedesk/press#4601.
	"""

	def tearDown(self):
		frappe.db.rollback()
		self._delete_groups()

	def _delete_groups(self):
		"""Remove the groups these tests created.

		`execute` commits, and a commit defeats `tearDown`'s rollback, so the
		rows would otherwise survive in the site. That is not cosmetic: other
		tests count Release Groups, so a leak makes `test_bench` fail for a
		reason that has nothing to do with them.
		"""
		groups = frappe.get_all(
			"Release Group", filters={"title": ["like", "Test ReleaseGroup%"]}, pluck="name"
		)
		if groups:
			frappe.db.delete("Release Group", {"name": ("in", groups)})
		frappe.db.commit()

	def _group(self, version="Version 15", **flags):
		# A Release Group validates that its first app is frappe, so a group
		# needs a real source rather than just a version.
		apps = [create_test_app("frappe")]
		group = create_test_release_group(apps, frappe_version=version)
		for field in FLAG_FIELDS:
			if field in flags:
				frappe.db.set_value("Release Group", group.name, field, flags[field])
		frappe.db.commit()
		return group

	def _clear_flags(self, group):
		frappe.db.set_value("Release Group", group.name, {field: 0 for field in FLAG_FIELDS})
		frappe.db.commit()

	def test_version_15_gets_workerpool_flags(self):
		flags = default_feature_flags("Version 15", 15)
		self.assertEqual(flags["use_rq_workerpool"], True)
		self.assertEqual(flags["gunicorn_threads_per_worker"], "4")
		self.assertEqual(flags["merge_default_and_short_rq_queues"], True)

	def test_version_16_gets_the_same_flags_as_15(self):
		"""The flags are keyed on `>= 15`, not on the exact version.

		Regression guard for #4601, which is that V16 was expected to fall
		through a version check that stopped at 15.
		"""
		self.assertEqual(default_feature_flags("Version 16", 16), default_feature_flags("Version 15", 15))

	def test_version_14_gets_only_the_queue_merge(self):
		flags = default_feature_flags("Version 14", 14)
		self.assertEqual(flags, {"merge_default_and_short_rq_queues": True})

	def test_version_13_gets_nothing(self):
		self.assertEqual(default_feature_flags("Version 13", 13), {})

	def test_unknown_version_number_gets_nothing(self):
		"""A version the fixture does not know must not be guessed at."""
		self.assertEqual(default_feature_flags("Version 99", 0), {})

	def test_version_number_lookup_is_actually_a_mapping(self):
		"""Guard on how the patch reads `Frappe Version`.

		It needs name -> number, not a mangled dict. `dict(get_all(...))` on a
		list of dicts iterates each row's keys and yields something like
		{'name': 'number'}, which makes every lookup return 0 and turns the
		patch into a no-op that still exits 0.
		"""
		mapping = {
			row.name: row.number
			for row in frappe.get_all("Frappe Version", fields=["name", "number"], limit_page_length=0)
		}
		self.assertEqual(mapping.get("Version 16"), 16)

	def test_patch_backfills_an_existing_group(self):
		group = self._group(version="Version 16")
		self._clear_flags(group)

		execute()

		flags = frappe.db.get_value("Release Group", group.name, FLAG_FIELDS, as_dict=True)
		self.assertEqual(flags.use_rq_workerpool, 1)
		# Int, not str: MariaDB casts the "4" from default_feature_flags.
		self.assertEqual(flags.gunicorn_threads_per_worker, 4)
		self.assertEqual(flags.merge_default_and_short_rq_queues, 1)

	def test_patch_leaves_a_deliberate_choice_alone(self):
		"""An operator's setting must not be overwritten by a default."""
		group = self._group(version="Version 16", gunicorn_threads_per_worker=8)

		execute()

		self.assertEqual(frappe.db.get_value("Release Group", group.name, "gunicorn_threads_per_worker"), 8)

	def test_patch_leaves_version_14_without_workerpool(self):
		group = self._group(version="Version 14")
		self._clear_flags(group)

		execute()

		flags = frappe.db.get_value("Release Group", group.name, FLAG_FIELDS, as_dict=True)
		self.assertEqual(flags.use_rq_workerpool, 0)
		self.assertEqual(flags.gunicorn_threads_per_worker, 0)
		self.assertEqual(flags.merge_default_and_short_rq_queues, 1)
