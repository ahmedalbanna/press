# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PressAccountSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		language: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		theme: DF.Link | None
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		if self.user != frappe.session.user and not _is_privileged():
			# Everyone may only ever see and change their own row.
			frappe.throw("You can only change your own account settings.", frappe.PermissionError)

		if self.language:
			self._validate_selectable("Press Language", self.language)
		if self.theme:
			self._validate_selectable("Press Theme", self.theme)

	def _validate_selectable(self, doctype: str, name: str):
		if not frappe.db.exists(doctype, name):
			frappe.throw(f"{doctype} {name!r} does not exist.")
		if not frappe.db.get_value(doctype, name, "enabled"):
			frappe.throw(f"{doctype} {name!r} is disabled.")


def _is_privileged() -> bool:
	return "System Manager" in frappe.get_roles()
