from contextlib import contextmanager

import frappe
from frappe import _

if frappe.TYPE_CHECKING:
	from frappe.core.doctype.user.user import User


def is_system_manager(user: str | None = None) -> bool:
	"""
	Checks if the given user is a system manager.

	:param user: User to check. If None, uses the current session user.
	:return: True if the user is a system manager, False otherwise.
	"""
	user = user or frappe.session.user
	user_doc: User = frappe.get_cached_doc("User", user)
	# FIX: Do not consider system users as system managers.
	# TODO: Remove system users from being considered as system managers.
	# HACK: Done to accommodate logics where system users are treated as system managers.
	return user_doc.user_type == "System User" or bool(user_doc.get("roles", {"role": "System Manager"}))


def is_desk_user(user: str | None = None) -> bool:
	"""
	Checks if the given user is a system user.

	:param user: User to check. If None, uses the current session user.
	:return: True if the user is a system user, False otherwise.
	"""
	user = user or frappe.session.user
	user_doc: User = frappe.get_cached_doc("User", user)
	return user_doc.user_type == "System User"


@contextmanager
def user_language(user: str | None = None):
	"""Run a block with the user's preferred language active.

	Used when sending emails so the recipient sees
	content in their own language.
	"""
	user = user or frappe.session.user
	language = frappe.db.get_value("User", user, "language") or "en"
	original = frappe.local.lang
	frappe.local.lang = language
	try:
		yield
	finally:
		frappe.local.lang = original


def send_user_email(user: str | None = None, **kwargs) -> None:
	"""Send an email in the recipient's language.

	Subjects are passed to sendmail verbatim and never rendered through Jinja,
	so translate them with `_()` inside this call rather than before it.

	Recipients may be a list or come from Communication records, in which case
	pass the owning User and they are resolved here.
	"""
	recipients = kwargs.get("recipients")
	if not isinstance(recipients, (list, tuple)):
		recipients = [recipients]
	user = user or (recipients[0] if recipients else None)

	with user_language(user):
		subject = kwargs.get("subject")
		if subject:
			kwargs["subject"] = _(subject)
		frappe.sendmail(**kwargs)
