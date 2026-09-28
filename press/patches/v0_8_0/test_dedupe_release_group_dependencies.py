import json
from unittest.mock import Mock, patch

import frappe
from frappe.core.utils import find
from frappe.tests.utils import FrappeTestCase

from press.api.bench import update_dependencies
from press.patches.v0_8_0.bump_v16_bench_version_to_5_31_0 import (
	execute as bump_v16,
)
from press.patches.v0_8_0.dedupe_release_group_dependencies import (
	execute as dedupe,
)
from press.patches.v0_8_0.dedupe_release_group_dependencies import version_key
from press.press.doctype.app.test_app import create_test_app
from press.press.doctype.release_group.test_release_group import (
	create_test_release_group,
)
from press.press.doctype.team.test_team import create_test_press_admin_team
from press.utils import get_current_team


@patch.object(frappe.db, "commit", new=Mock())
class TestDedupeReleaseGroupDependencies(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.team = create_test_press_admin_team()
		self.app = create_test_app()
		self.app.add_source(
			frappe_version="Version 16",
			repository_url="https://github.com/frappe/frappe",
			branch="version-16",
			team=get_current_team(),
			public=True,
		)
		self.group = create_test_release_group([self.app], frappe_version="Version 16")

	def tearDown(self):
		frappe.db.rollback()

	def versions(self, dependency):
		self.group.reload()
		return sorted(d.version for d in self.group.dependencies if d.dependency == dependency)

	def add_duplicate(self, dependency, version):
		"""Add a second row for a dependency, the way the bump patches used to."""
		self.group.append("dependencies", {"dependency": dependency, "version": version})
		self.group.save(ignore_permissions=True)

	def test_group_starts_with_one_row_per_dependency(self):
		self.assertEqual(self.versions("BENCH_VERSION"), ["5.31.0"])

	def test_version_key_orders_versions_numerically(self):
		self.assertLess(version_key("5.9.0"), version_key("5.31.0"))
		self.assertLess(version_key("3.10"), version_key("3.14"))
		self.assertEqual(version_key("5.31.0-rc1"), version_key("5.31.0"))

	def test_dedupe_keeps_the_highest_version(self):
		self.add_duplicate("BENCH_VERSION", "5.27.0")
		self.add_duplicate("NODE_VERSION", "14.19.0")

		dedupe()

		self.assertEqual(self.versions("BENCH_VERSION"), ["5.31.0"])
		self.assertEqual(self.versions("NODE_VERSION"), ["24.12.0"])

	def test_dedupe_keeps_one_row_when_versions_match(self):
		self.add_duplicate("PIP_VERSION", "25.3")

		dedupe()

		self.assertEqual(self.versions("PIP_VERSION"), ["25.3"])

	def test_dedupe_is_a_noop_without_duplicates(self):
		before = sorted((d.dependency, d.version) for d in self.group.dependencies)

		dedupe()

		self.group.reload()
		after = sorted((d.dependency, d.version) for d in self.group.dependencies)
		self.assertEqual(before, after)

	def test_dependencies_can_be_edited_again_after_dedupe(self):
		"""The point of the patch: duplicate keys lock a group out of editing."""
		self.add_duplicate("BENCH_VERSION", "5.27.0")
		dedupe()
		self.group.reload()  # the dedupe deleted a row, so the in-memory copy is stale

		dependencies = [{"key": d.dependency, "value": d.version} for d in self.group.dependencies]
		find(dependencies, lambda d: d["key"] == "BENCH_VERSION")["value"] = "5.30.0"
		update_dependencies(self.group.name, json.dumps(dependencies))

		self.assertEqual(self.versions("BENCH_VERSION"), ["5.30.0"])

	def test_bump_patch_does_not_create_a_second_row(self):
		"""The bump patch must drop the stale row, not append a second one."""
		self.add_duplicate("BENCH_VERSION", "5.27.0")

		bump_v16()

		self.assertEqual(self.versions("BENCH_VERSION"), ["5.31.0"])
