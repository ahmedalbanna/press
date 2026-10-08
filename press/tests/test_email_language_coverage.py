"""Enforces that customer-facing email honours the recipient's language.

Story 8 is easy to break silently: `frappe.sendmail` works perfectly well and
sends English, so nothing fails when a call site forgets the language context.
The recipients below are the audited exception list -- internal operations
alerts with no customer User to read a language preference. Everything else
must go through `send_user_email` or `user_language`.

To add a call site to the exception list, state why the recipient has no
language preference. That is the only reason that belongs here.
"""

import ast
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

from press.utils.user import send_user_email, user_language

APP_ROOT = Path(frappe.get_app_path("press"))

# path (relative to press/) -> why the recipient is not a customer
UNWRAPPED_EXCEPTIONS = {
	"press/doctype/alertmanager_webhook_log/alertmanager_webhook_log.py": (
		"alerts to the on-call mailbox configured for Alertmanager, not a Press User"
	),
}


def _sendmail_calls(root: Path):
	"""Yield (relative_path, lineno, wrapped) for every frappe.sendmail call."""
	for path in sorted(root.rglob("*.py")):
		if "tests" in path.parts:
			continue
		source = path.read_text()
		if "frappe.sendmail" not in source:
			continue
		tree = ast.parse(source)
		parent = {}
		for node in ast.walk(tree):
			for child in ast.iter_child_nodes(node):
				parent[child] = node
		for node in ast.walk(tree):
			if not (
				isinstance(node, ast.Call)
				and isinstance(node.func, ast.Attribute)
				and node.func.attr == "sendmail"
			):
				continue
			cursor, wrapped = node, False
			while cursor in parent:
				cursor = parent[cursor]
				if isinstance(cursor, ast.With):
					for item in cursor.items:
						call = item.context_expr
						name = getattr(call, "id", None) or getattr(getattr(call, "func", None), "id", None)
						if name == "user_language":
							wrapped = True
			yield path.relative_to(root).as_posix(), node.lineno, wrapped


class TestCustomerEmailsHonourLanguage(FrappeTestCase):
	def test_every_customer_facing_sendmail_respects_the_language_context(self):
		unwrapped = {}
		for rel, lineno, wrapped in _sendmail_calls(APP_ROOT):
			if wrapped or rel in UNWRAPPED_EXCEPTIONS:
				continue
			unwrapped.setdefault(rel, []).append(lineno)

		self.assertEqual(
			unwrapped,
			{},
			"customer-facing sendmail without a language context; use "
			"send_user_email(user, ...), or add the file to "
			"UNWRAPPED_EXCEPTIONS with a reason",
		)

	def test_every_exception_still_states_a_reason(self):
		for rel in UNWRAPPED_EXCEPTIONS:
			self.assertTrue(
				UNWRAPPED_EXCEPTIONS[rel].strip(),
				f"{rel} is allowlisted with no reason",
			)
			self.assertTrue((APP_ROOT / rel).exists(), f"allowlisted {rel} does not exist")

	def test_no_exception_is_actually_wrapped(self):
		# An allowlisted file that starts wrapping its emails should come off
		# the list, or the exception becomes a way to skip the real check.
		for rel, _, wrapped in _sendmail_calls(APP_ROOT):
			if rel in UNWRAPPED_EXCEPTIONS and wrapped:
				self.fail(f"{rel} is allowlisted but now wraps sendmail; drop it")


class TestSendUserEmailHelper(FrappeTestCase):
	"""Uses a real User so the language comes from the database, as in production.

	Against a made-up address the lookup falls back to `en`, which would make
	these pass or fail for the wrong reason.
	"""

	ARABIC_SUBJECT = "Settle invoices"

	def setUp(self):
		super().setUp()
		self.user = frappe.get_doc(
			{
				"doctype": "User",
				"name": "arabic-recipient@example.com",
				"email": "arabic-recipient@example.com",
				"first_name": "Arabic",
				"language": "ar",
				"enabled": 1,
				"user_type": "System User",
			}
		).insert(ignore_permissions=True)
		self.sent = {}
		self.original_sendmail = frappe.sendmail

	def tearDown(self):
		frappe.sendmail = self.original_sendmail
		frappe.local.lang = "en"
		super().tearDown()

	def _capture(self, **kwargs):
		frappe.sendmail = lambda **kw: self.sent.update(kw, _lang=frappe.local.lang)
		send_user_email(self.user.name, **kwargs)
		return self.sent

	def test_send_user_email_translates_the_subject(self):
		sent = self._capture(recipients=self.user.name, subject=self.ARABIC_SUBJECT)
		self.assertEqual(sent["subject"], "سداد الفواتير")
		self.assertEqual(sent["_lang"], "ar")

	def test_send_user_email_leaves_an_unknown_subject_intact(self):
		sent = self._capture(recipients=self.user.name, subject="A string nobody translated")
		self.assertEqual(sent["subject"], "A string nobody translated")

	def test_send_user_email_restores_the_caller_language(self):
		frappe.local.lang = "ar"
		self._capture(recipients=self.user.name, subject=self.ARABIC_SUBJECT)
		self.assertEqual(frappe.local.lang, "ar")

	def test_send_user_email_accepts_a_recipient_list(self):
		sent = self._capture(
			recipients=[self.user.name, "second@example.com"],
			subject=self.ARABIC_SUBJECT,
		)
		self.assertEqual(sent["recipients"], [self.user.name, "second@example.com"])
		self.assertEqual(sent["subject"], "سداد الفواتير")

	def test_send_user_email_falls_back_to_english_for_an_unknown_user(self):
		# Must pass the ghost address as the user, not the Arabic one, or the
		# fallback path is never exercised.
		frappe.sendmail = lambda **kw: self.sent.update(kw, _lang=frappe.local.lang)
		send_user_email(
			"ghost@example.com",
			recipients="ghost@example.com",
			subject=self.ARABIC_SUBJECT,
		)
		self.assertEqual(self.sent["_lang"], "en")
		self.assertEqual(self.sent["subject"], self.ARABIC_SUBJECT)

	def test_send_user_email_derives_the_user_from_recipients(self):
		# Many call sites pass None because the recipient arrives through
		# Communication records rather than a variable.
		frappe.sendmail = lambda **kw: self.sent.update(kw, _lang=frappe.local.lang)
		send_user_email(None, recipients=self.user.name, subject=self.ARABIC_SUBJECT)
		self.assertEqual(self.sent["_lang"], "ar")
		self.assertEqual(self.sent["subject"], "سداد الفواتير")


class TestUserLanguageUnchanged(FrappeTestCase):
	def test_user_language_is_still_the_escape_hatch_for_blocks(self):
		# Some call sites build args across several statements, so the context
		# manager stays public alongside the helper.
		self.assertTrue(callable(user_language))
		self.assertTrue(callable(send_user_email))
