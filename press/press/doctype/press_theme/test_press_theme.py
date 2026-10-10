# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import re
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

from press.press.doctype.press_theme.press_theme import get_default_theme

GLOBAL_CSS = Path(frappe.get_app_path("press")).parent / "dashboard" / "src" / "styles" / "global.css"


def read_stylesheet_tokens(css: str, selector: str) -> dict:
	"""Token name to value for one theme, as the stylesheet cascades them.

	The stylesheet declares the same selector more than once, so the blocks are
	merged in document order and a later value wins, exactly as the browser
	does. This is what lets the seeded Theme rows be compared to the CSS.
	"""
	tokens = {}
	for match in re.finditer(rf"(?m)^{re.escape(selector)}\s*\{{", css):
		block = _balanced_block(css, match.end())
		for name, value in re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block):
			tokens[name.strip()] = value.strip()
	return tokens


def _balanced_block(css: str, start: int) -> str:
	depth = 1
	position = start
	while position < len(css) and depth:
		if css[position] == "{":
			depth += 1
		elif css[position] == "}":
			depth -= 1
		position += 1
	return css[start : position - 1]


class TestPressTheme(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_the_seeded_default_theme_is_offered_as_the_default(self):
		self.assertEqual(get_default_theme(), "light")
		self.assertEqual(frappe.db.get_value("Press Theme", "light", "is_default"), 1)

	def test_setting_a_second_default_clears_the_first(self):
		dark = frappe.get_doc("Press Theme", "dark")
		dark.is_default = 1
		dark.save(ignore_permissions=True)
		self.assertEqual(get_default_theme(), "dark")
		self.assertEqual(frappe.db.get_value("Press Theme", "light", "is_default"), 0)

	def test_the_only_enabled_default_theme_cannot_be_unset(self):
		dark = frappe.get_doc("Press Theme", "dark")
		dark.enabled = 0
		dark.save(ignore_permissions=True)
		theme = frappe.get_doc("Press Theme", "light")
		theme.is_default = 0
		with self.assertRaises(frappe.ValidationError) as context:
			theme.save()

		self.assertIn(
			"At least one enabled theme must be the default",
			str(context.exception),
		)

	def test_disabling_the_only_enabled_default_theme_is_refused(self):
		theme = frappe.get_doc("Press Theme", "light")
		theme.enabled = 0
		with self.assertRaises(frappe.ValidationError) as context:
			theme.save()

		self.assertIn(
			"At least one enabled theme must be the default",
			str(context.exception),
		)

	def test_a_theme_name_is_normalised_to_a_css_safe_value(self):
		theme = frappe.get_doc({"doctype": "Press Theme", "theme_name": "Solar Flare"})
		theme.insert(ignore_permissions=True)
		self.assertEqual(theme.theme_name, "solar-flare")

	def test_a_repeated_token_is_refused(self):
		theme = frappe.get_doc(
			{
				"doctype": "Press Theme",
				"theme_name": "duplicate-tokens",
				"tokens": [
					{"token_name": "surface-gray-1", "token_value": "#ffffff"},
					{"token_name": "surface-gray-1", "token_value": "#000000"},
				],
			}
		)
		with self.assertRaises(frappe.ValidationError) as context:
			theme.insert(ignore_permissions=True)

		self.assertIn("is listed more than once", str(context.exception))

	def test_an_empty_token_value_is_refused(self):
		# token_value is `reqd`, so Frappe refuses it before saving.
		theme = frappe.get_doc(
			{
				"doctype": "Press Theme",
				"theme_name": "empty-token",
				"tokens": [{"token_name": "surface-gray-1", "token_value": ""}],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			theme.insert(ignore_permissions=True)

	def test_the_light_theme_reproduces_the_stylesheet(self):
		self.assertEqual(
			frappe.get_doc("Press Theme", "light").token_map(),
			read_stylesheet_tokens(GLOBAL_CSS.read_text(), ":root"),
		)

	def test_the_dark_theme_reproduces_the_stylesheet(self):
		self.assertEqual(
			frappe.get_doc("Press Theme", "dark").token_map(),
			read_stylesheet_tokens(GLOBAL_CSS.read_text(), '[data-theme="dark"]'),
		)
