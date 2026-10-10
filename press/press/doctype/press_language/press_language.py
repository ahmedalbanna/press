# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# Languages written right-to-left. Anything not listed is treated as ltr.
RTL_LANGUAGES = {"ar", "fa", "he", "ur", "ps", "sd", "yi", "dv"}


class PressLanguage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		direction: DF.Literal["ltr", "rtl"]
		enabled: DF.Check
		english_name: DF.Data | None
		is_default: DF.Check
		language_code: DF.Data
		language_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	def before_naming(self):
		# `autoname` reads language_code as typed, so normalise before the name
		# is built or the stored name and the field would disagree.
		self.language_code = self._normalised_code(self.language_code)

	def validate(self):
		self.language_code = self._normalised_code(self.language_code)
		if not self.language_code:
			frappe.throw("Language Code is required.")

		if not self.english_name:
			self.english_name = self.language_name

		if self.direction not in ("ltr", "rtl"):
			frappe.throw("Direction must be either ltr or rtl.")

	@staticmethod
	def _normalised_code(value: str | None) -> str:
		return (value or "").strip().lower()

	def before_save(self):
		if self.is_default and self.has_value_changed("is_default"):
			# A second default would leave two languages fighting over what a
			# new account opens in.
			self._clear_other_defaults()

		self._ensure_a_default_remains()

	def on_trash(self):
		if self.is_default:
			frappe.throw("The default language cannot be deleted.")

		# Accounts left pointing at a deleted language fall back to the default
		# rather than breaking the dashboard's language picker.
		frappe.db.sql(
			"""
			UPDATE `tabAccount Settings`
			SET language = %(default)s
			WHERE language = %(deleted)s
			""",
			{"default": get_default_language(), "deleted": self.name},
		)

	def _clear_other_defaults(self):
		frappe.db.set_value(
			"Press Language",
			{"is_default": 1, "name": ("!=", self.name)},
			"is_default",
			0,
		)

	def _ensure_a_default_remains(self):
		if self.is_default and self.enabled:
			return
		has_other_default = frappe.db.exists(
			"Press Language",
			{"is_default": 1, "enabled": 1, "name": ("!=", self.name)},
		)
		if not has_other_default:
			frappe.throw(
				"At least one enabled language must be the default. Set another language as the default first."
			)


def get_default_language() -> str:
	"""The language code a new account should start in."""
	language = frappe.db.get_value("Press Language", {"is_default": 1, "enabled": 1}, "language_code")
	return language or "en"
