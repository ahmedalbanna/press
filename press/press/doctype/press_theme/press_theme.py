# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PressTheme(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		enabled: DF.Check
		is_default: DF.Check
		label: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		theme_name: DF.Data
		tokens: DF.Table[PressThemeToken]
	# end: auto-generated types

	def before_naming(self):
		# `autoname` reads theme_name as typed, so normalise before the name is
		# built or the stored name and the field would disagree.
		self.theme_name = self._normalised_theme_name(self.theme_name)

	def validate(self):
		self.theme_name = self._normalised_theme_name(self.theme_name)
		if not self.theme_name:
			frappe.throw("Theme Name is required.")
		if not (self.label or "").strip():
			self.label = self.theme_name.replace("-", " ").title()

		self._reject_duplicate_tokens()

	@staticmethod
	def _normalised_theme_name(value: str | None) -> str:
		return (value or "").strip().lower().replace(" ", "-")

	def before_save(self):
		if self.is_default and self.has_value_changed("is_default"):
			# A second default would leave two themes fighting over what a new
			# account opens in.
			self._clear_other_defaults()

		self._ensure_a_default_remains()

	def on_trash(self):
		if self.is_default:
			frappe.throw("The default theme cannot be deleted.")

		# Accounts left pointing at a deleted theme fall back to the default
		# rather than breaking the dashboard's theme picker.
		frappe.db.sql(
			"""
			UPDATE `tabPress Account Settings`
			SET theme = %(default)s
			WHERE theme = %(deleted)s
			""",
			{"default": get_default_theme(), "deleted": self.name},
		)

	def token_map(self) -> dict:
		"""Token name to value, for the dashboard to turn into CSS variables."""
		return {token.token_name: token.token_value for token in (self.tokens or [])}

	def _reject_duplicate_tokens(self):
		# A repeated token would silently win by row order, which is confusing
		# to debug in a 50-row grid.
		seen = set()
		for token in self.tokens or []:
			if token.token_name in seen:
				frappe.throw(
					f"Token {token.token_name!r} is listed more than once. Each token may appear only once per theme."
				)
			seen.add(token.token_name)

	def _clear_other_defaults(self):
		frappe.db.set_value("Press Theme", {"is_default": 1, "name": ("!=", self.name)}, "is_default", 0)

	def _ensure_a_default_remains(self):
		if self.is_default and self.enabled:
			return
		has_other_default = frappe.db.exists(
			"Press Theme", {"is_default": 1, "enabled": 1, "name": ("!=", self.name)}
		)
		if not has_other_default:
			frappe.throw(
				"At least one enabled theme must be the default. Set another theme as the default first."
			)


def get_default_theme() -> str:
	"""The theme name a new account should start in."""
	theme = frappe.db.get_value("Press Theme", {"is_default": 1, "enabled": 1}, "theme_name")
	return theme or "light"
