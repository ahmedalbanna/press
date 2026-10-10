# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from press.utils.preferences import (
	get_account_settings,
	get_languages,
	get_themes,
	set_language,
	set_theme,
)


class TestPressAccountSettings(FrappeTestCase):
	def tearDown(self):
		# `frappe.set_user` is request state, so only the writes roll back and
		# the switched user would leak into the next test.
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_a_new_user_gets_the_default_language_and_theme(self):
		user = create_test_press_user("preferences-defaults@example.com")
		settings = get_account_settings(user)
		self.assertEqual(settings["language"], "en")
		self.assertEqual(settings["theme"], "light")
		self.assertEqual(settings["direction"], "ltr")

	def test_switching_language_updates_the_account_and_the_user_record(self):
		create_test_press_user("preferences-language@example.com")
		settings = set_language("ar")
		self.assertEqual(settings["language"], "ar")
		self.assertEqual(settings["direction"], "rtl")
		self.assertEqual(frappe.db.get_value("User", frappe.session.user, "language"), "ar")

	def test_switching_theme_updates_the_account(self):
		create_test_press_user("preferences-theme@example.com")
		settings = set_theme("dark")
		self.assertEqual(settings["theme"], "dark")

	def test_an_unknown_language_is_refused(self):
		create_test_press_user("preferences-unknown-language@example.com")
		with self.assertRaises(frappe.ValidationError) as context:
			set_language("zz")
		self.assertIn("does not exist", str(context.exception))

	def test_a_disabled_language_is_refused(self):
		create_test_press_user("preferences-disabled-language@example.com")
		frappe.db.set_value("Press Language", "ar", "enabled", 0)
		with self.assertRaises(frappe.ValidationError) as context:
			set_language("ar")
		self.assertIn("is disabled", str(context.exception))

	def test_a_disabled_theme_is_refused(self):
		create_test_press_user("preferences-disabled-theme@example.com")
		frappe.db.set_value("Press Theme", "dark", "enabled", 0)
		with self.assertRaises(frappe.ValidationError) as context:
			set_theme("dark")
		self.assertIn("is disabled", str(context.exception))

	def test_only_enabled_languages_are_offered(self):
		frappe.db.set_value("Press Language", "ar", "enabled", 0)
		codes = [entry["language_code"] for entry in get_languages()]
		self.assertEqual(codes, ["en"])

	def test_offered_themes_carry_their_tokens(self):
		themes = {entry["theme_name"]: entry for entry in get_themes()}
		self.assertEqual(set(themes), {"light", "dark"})
		self.assertEqual(len(themes["light"]["tokens"]), 36)
		self.assertEqual(themes["dark"]["tokens"]["surface-menu-bar"], "#020617")

	def test_a_user_cannot_change_another_users_settings(self):
		create_test_press_user("preferences-victim@example.com")
		create_test_press_user("preferences-other@example.com")
		frappe.set_user("preferences-other@example.com")
		settings = frappe.get_doc("Press Account Settings", "preferences-victim@example.com")
		settings.theme = "dark"
		with self.assertRaises(frappe.PermissionError) as context:
			settings.save()
		self.assertIn("You can only change your own account settings", str(context.exception))

	def test_a_user_reading_their_own_settings_is_allowed(self):
		create_test_press_user("preferences-own@example.com")
		frappe.set_user("preferences-own@example.com")
		settings = frappe.get_doc("Press Account Settings", frappe.session.user)
		settings.theme = "dark"
		settings.save()
		self.assertEqual(get_account_settings()["theme"], "dark")


def create_test_press_user(email: str) -> str:
	"""A user holding the Press User role, so the doctype permission layer lets
	a save through and our own ownership guard is what refuses it."""
	if not frappe.db.exists("User", email):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": email.split("@")[0],
				"send_welcome_email": 0,
				"roles": [{"role": "Press User"}],
			}
		).insert(ignore_permissions=True)
		user = user.name
	else:
		user = email

	if not frappe.db.exists("Press Account Settings", user):
		frappe.get_doc(
			{
				"doctype": "Press Account Settings",
				"user": user,
				"language": "en",
				"theme": "light",
			}
		).insert(ignore_permissions=True)
	return user
