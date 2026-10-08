"""Regression tests for Arabic email delivery.

Story 8 asks for emails in the recipient's language. That chain has four links
and every one of them can be broken silently, so each is asserted here:

1. the template marks its copy translatable with `_()`
2. the catalog actually resolves those strings for `ar`
3. `user_language` is applied around the sendmail call
4. the rendered HTML is Arabic, not English

The catalog is a CSV, so a comma inside a sentence silently shifts every
column after it and the strings stop matching with no error anywhere. That is
the failure mode test_email_catalog_resolves_every_marked_string guards.
"""

import re
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.translate import get_translations_from_csv
from frappe.utils.jinja import get_email_from_template

from press.press.doctype.team.suspend_sites import suspend_sites_and_send_email
from press.utils.user import user_language

CATALOG_LANG = "ar"

# Templates whose copy is marked translatable and seeded in the catalog. Every
# string they mark must resolve, or the Arabic render silently falls back to
# English for that line only.
TRANSLATED_TEMPLATES = (
	"suspended_sites",
	"payment_failed",
	"insufficient_balance",
	"site_backup_failed",
	"reset_password",
	"one_time_login_link",
	"verification_code_for_login",
	"login_otp",
	"admin_login",
	"disabled_site_monitoring",
	"2fa_recovery_codes_viewed",
	"2fa_recovery_codes_yearly_reminder",
)

RENDER_CASES = {
	"suspended_sites": {
		"subject": "تم تعليق مواقعك على AlbannaTech",
		"sites": ["acme.example.com"],
		"billing_link": "https://press.localhost/dashboard/billing",
		"site_url": "https://press.localhost",
	},
	"payment_failed": {
		"subject": "x",
		"payment_link": "https://pay",
		"amount": "$25.00",
		"account_update_link": "https://billing",
		"card_not_added": False,
		"last_4": "4242",
		"sites": ["acme.example.com"],
	},
	"insufficient_balance": {},
	"site_backup_failed": {"site_name": "acme.example.com"},
	"reset_password": {"link": "https://reset", "read_pixel_path": None},
	"one_time_login_link": {"link": "https://login", "minutes": 10},
	"verification_code_for_login": {"full_name": "Sara", "otp": "123456"},
	"login_otp": {"otp": "123456", "read_pixel_path": None},
	"admin_login": {"user": "Ali", "site": "acme.com", "reason": "support ticket"},
	"disabled_site_monitoring": {"site": "acme.com", "reason": "over quota"},
	"2fa_recovery_codes_viewed": {"viewed_at": "2026-10-08", "link": "https://s"},
	"2fa_recovery_codes_yearly_reminder": {"link": "https://s"},
}

# English that must never survive into an Arabic render of these templates.
# Includes the label copy passed to utils.button / utils.link, which is where a
# partial translation tends to leave the call to action in English.
ENGLISH_SENTINELS = (
	"Payment of",
	"Update Billing Settings",
	"Pay Invoice Now",
	"Following sites were suspended",
	"Insufficient balance",
	"Greetings from",
	"All attempts to back up",
	"Please click on the button",
	"Click the following button",
	"You have requested a verification code",
	"Use below verification code",
	"just logged in to your site",
	"Monitoring & alerting mechanism",
	"Security Alert",
	"Hey there!",
	"Change your password",
	"It's been a year",
	"View Your Recovery Codes",
)


def visible_text(html: str) -> str:
	return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


class TestArabicEmailCatalog(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()
		from frappe.translate import clear_cache

		clear_cache()
		super().tearDown()

	def _catalog(self) -> dict:
		return get_translations_from_csv(CATALOG_LANG, "press")

	def test_catalog_file_exists_and_is_not_empty(self):
		self.assertTrue(self._catalog(), f"{CATALOG_LANG}.csv resolved to no entries")

	def test_catalog_columns_are_not_shifted(self):
		# A comma inside a sentence shifts the columns, and the signature is
		# translation text landing in the source column. Keys are English.
		catalog = self._catalog()
		arabic = re.compile(r"[؀-ۿ]")
		for source, translated in catalog.items():
			self.assertIsNone(arabic.search(source), f"shifted column, CSV needs quoting: {source!r}")
			self.assertTrue(translated.strip(), f"empty translation for {source!r}")
			self.assertIsNotNone(arabic.search(translated), f"{source!r} has no Arabic translation")

	def test_suspended_sites_strings_all_resolve(self):
		catalog = self._catalog()
		template = (
			Path(frappe.get_app_path("press")).joinpath("templates/emails/suspended_sites.html").read_text()
		)
		marked = set(re.findall(r"_\(\s*[\"'](.+?)[\"']\s*\)", template))
		self.assertTrue(marked, "no _() markers found in suspended_sites.html")
		missing = marked - set(catalog)
		self.assertEqual(missing, set(), f"marked but untranslated: {missing}")

	def test_suspension_subject_is_translated(self):
		self.assertIn("Your sites have been suspended on AlbannaTech", self._catalog())

	def test_every_translated_template_has_its_strings_in_the_catalog(self):
		# Guards the gap where a template is marked translatable but its copy
		# was never added, which renders English with no error.
		catalog = self._catalog()
		app = Path(frappe.get_app_path("press"))
		for name in TRANSLATED_TEMPLATES:
			source = (app / "templates" / "emails" / f"{name}.html").read_text()
			marked = set(re.findall(r"_\(\s*[\"'](.+?)[\"']\s*\)", source))
			self.assertTrue(marked, f"{name}.html marks nothing translatable")
			missing = marked - set(catalog)
			self.assertEqual(missing, set(), f"{name}.html untranslated: {missing}")

	def test_catalog_contains_no_foreign_script(self):
		# Guards a stray character from another script, which renders as a box
		# in the customer's mail client and is easy to miss in a diff review.
		# Latin is allowed: the brand name stays Latin inside Arabic copy.
		foreign = re.compile(r"[Ͱ-ϿЀ-ӿ฀-鿿가-힯]")
		for source, translated in self._catalog().items():
			self.assertIsNone(
				foreign.search(translated),
				f"non-Arabic script in the translation of {source!r}",
			)


class TestArabicEmailRendering(FrappeTestCase):
	"""Renders the template the way a real Arabic send would, via the catalog."""

	def setUp(self):
		super().setUp()
		self.original_lang = frappe.local.lang

	def tearDown(self):
		frappe.local.lang = self.original_lang
		from frappe.translate import clear_cache

		clear_cache()
		super().tearDown()

	def _render(self) -> str:
		frappe.local.lang = CATALOG_LANG
		from frappe.translate import clear_cache

		clear_cache()
		html, _ = get_email_from_template(
			"suspended_sites",
			{
				"subject": "تم تعليق مواقعك على AlbannaTech",
				"sites": ["acme.example.com"],
				"billing_link": "https://press.localhost/dashboard/billing",
				"site_url": "https://press.localhost",
			},
		)
		return visible_text(html)

	def test_body_renders_arabic_not_english(self):
		text = self._render()
		self.assertIn("للأسف", text)
		self.assertIn("سداد الفواتير", text)
		self.assertIn("فريق الدعم", text)

	def test_no_english_copy_leaks_into_the_arabic_render(self):
		text = self._render()
		for leaked in (
			"Unfortunately",
			"Settle invoices",
			"concerns or questions",
			"were suspended:",
			"Once your invoices",
		):
			self.assertNotIn(leaked, text)

	def test_site_links_point_at_the_press_domain_not_frappe_cloud(self):
		frappe.local.lang = CATALOG_LANG
		from frappe.translate import clear_cache

		clear_cache()
		html, _ = get_email_from_template(
			"suspended_sites",
			{"subject": "x", "sites": ["acme.example.com"], "billing_link": "b", "site_url": "s"},
		)
		self.assertNotIn("cloud.frappe.io", html)

	def test_every_translated_template_renders_arabic(self):
		from frappe.translate import clear_cache

		for name, args in RENDER_CASES.items():
			frappe.local.lang = CATALOG_LANG
			clear_cache()
			html, _ = get_email_from_template(name, args)
			text = visible_text(html)
			with self.subTest(template=name):
				self.assertRegex(text, r"[؀-ۿ]", f"{name} rendered with no Arabic at all")
				for leaked in ENGLISH_SENTINELS:
					self.assertNotIn(leaked, text, f"{name} leaked {leaked!r}")

	def test_payment_failed_card_not_added_branch_also_renders_arabic(self):
		from frappe.translate import clear_cache

		frappe.local.lang = CATALOG_LANG
		clear_cache()
		args = dict(RENDER_CASES["payment_failed"], card_not_added=True, sites=[])
		html, _ = get_email_from_template("payment_failed", args)
		text = visible_text(html)
		self.assertIn("لم تُضِف بطاقة", text)
		self.assertNotIn("Update Billing Settings", text)


class TestUserLanguageContext(FrappeTestCase):
	def tearDown(self):
		frappe.local.lang = "en"
		super().tearDown()

	def test_user_language_sets_and_restores_the_requested_language(self):
		frappe.local.lang = "en"
		with user_language("someone@example.com"):
			self.assertEqual(frappe.local.lang, "en", "unknown user should fall back to en")

	def test_user_language_falls_back_rather_than_raising_for_ghost_users(self):
		frappe.local.lang = "ar"
		with user_language("does-not-exist@example.com"):
			self.assertEqual(frappe.local.lang, "en")
		self.assertEqual(frappe.local.lang, "ar", "must restore the outer language")


class TestSuspensionEmailBranding(FrappeTestCase):
	def test_suspend_sites_no_longer_names_frappe_cloud_to_customers(self):
		import inspect

		source = inspect.getsource(suspend_sites_and_send_email)
		self.assertNotIn("Frappe Cloud", source)
		self.assertIn("user_language", source, "suspension email must honour the user's language")
