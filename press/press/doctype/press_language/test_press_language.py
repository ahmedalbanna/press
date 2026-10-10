# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from press.press.doctype.press_language.press_language import (
	RTL_LANGUAGES,
	get_default_language,
)


def create_test_language(language_code: str, **kwargs) -> str:
	language = frappe.get_doc(
		{
			"doctype": "Press Language",
			"language_code": language_code,
			"language_name": kwargs.pop("language_name", language_code.title()),
			**kwargs,
		}
	).insert(ignore_permissions=True)
	return language.name


class TestPressLanguage(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_the_seeded_default_language_is_offered_as_the_default(self):
		self.assertEqual(get_default_language(), "en")
		self.assertEqual(frappe.db.get_value("Press Language", "en", "is_default"), 1)
		self.assertEqual(frappe.db.get_value("Press Language", "en", "enabled"), 1)

	def test_arabic_is_the_rtl_language(self):
		self.assertEqual(frappe.db.get_value("Press Language", "ar", "direction"), "rtl")
		self.assertEqual(frappe.db.get_value("Press Language", "ar", "is_default"), 0)
		self.assertIn("ar", RTL_LANGUAGES)

	def test_setting_a_second_default_clears_the_first(self):
		create_test_language("fr", is_default=1)
		self.assertEqual(get_default_language(), "fr")
		self.assertEqual(frappe.db.get_value("Press Language", "en", "is_default"), 0)

	def test_the_only_enabled_default_language_cannot_be_unset(self):
		frappe.db.set_value("Press Language", "ar", "enabled", 0)
		language = frappe.get_doc("Press Language", "en")
		language.is_default = 0
		with self.assertRaises(frappe.ValidationError) as context:
			language.save()

		self.assertIn(
			"At least one enabled language must be the default",
			str(context.exception),
		)

	def test_disabling_the_only_enabled_default_language_is_refused(self):
		language = frappe.get_doc("Press Language", "en")
		language.enabled = 0
		with self.assertRaises(frappe.ValidationError) as context:
			language.save()

		self.assertIn(
			"At least one enabled language must be the default",
			str(context.exception),
		)

	def test_an_unknown_direction_is_refused(self):
		language = frappe.get_doc("Press Language", "ar")
		language.direction = "sideways"
		with self.assertRaises(frappe.ValidationError) as context:
			language.save()

		self.assertIn("Direction must be either ltr or rtl", str(context.exception))

	def test_the_default_language_cannot_be_deleted(self):
		language = frappe.get_doc("Press Language", "en")
		with self.assertRaises(frappe.ValidationError) as context:
			language.delete()

		self.assertIn("The default language cannot be deleted", str(context.exception))

	def test_a_language_code_is_stored_lowercase(self):
		language = create_test_language("DE")
		self.assertEqual(frappe.db.get_value("Press Language", language), "de")

	def test_the_english_name_falls_back_to_the_native_name(self):
		create_test_language("es", language_name="Español")
		self.assertEqual(frappe.db.get_value("Press Language", "es", "english_name"), "Español")
