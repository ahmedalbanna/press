# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PressThemeToken(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		token_name: DF.Data
		token_value: DF.Data
	# end: auto-generated types

	def validate(self):
		self.token_name = (self.token_name or "").strip().lstrip("-").strip()
		if not self.token_name:
			frappe.throw("Token Name is required.")
		if " " in self.token_name:
			frappe.throw(
				f"Token Name cannot contain spaces: {self.token_name!r}. Use the CSS custom property name, e.g. surface-gray-1."
			)
