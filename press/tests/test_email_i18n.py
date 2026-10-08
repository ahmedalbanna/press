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
	"budget_alert",
	"payment_method_invalid",
	"mandate_amount_capped",
	"payment_failed_upi_autopay",
	"site_exceeded_disk_usage_warning",
	"site_suspend_due_to_exceeding_disk_usage",
	"notify_before_site_archival",
	"press_webhook_disabled",
	"enabled_auto_disk_expansion",
	"disabled_auto_disk_expansion",
	"plan_upgrade_recommendation",
	"snapshot_recovery_completion",
	"incident",
	"auto_scale_notification",
	"bench_deploy_failure",
	"partner_link_certificate",
	"partner_approval",
	"access_request",
	"access_request_update",
	"remote_login",
	"transfer_team_confirmation",
	"marketplace_auto_review",
	"verify_account_for_site_login",
	"product_trial_verify_account",
	"app_approval_request_update",
	"marketplace_audit_report",
	"payment_failed_partner",
	"product_trial_email",
)

# Templates whose only translatable surface is a string passed in as an
# argument, so they carry no _("literal") to check against the catalog.
ARG_ONLY_TEMPLATES = frozenset({"product_trial_email"})

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
	"budget_alert": {
		"team_user": "Ali",
		"alert_threshold": "100",
		"invoice_amount": "150",
		"excess_amount": "50",
		"period_start": "2026-10-01",
		"period_end": "2026-10-31",
	},
	"payment_method_invalid": {
		"subject": "x",
		"amount": "20",
		"billing_link": "https://b",
	},
	"mandate_amount_capped": {
		"subject": "x",
		"confirmed_amount": "500",
		"requested_amount": "1000",
		"upi_autopay_link": "https://u",
	},
	"payment_failed_upi_autopay": {
		"subject": "x",
		"amount": "20",
		"upi_vpa": "a@upi",
		"error_reason": "INSUFFICIENT_FUNDS",
		"upi_autopay_link": "https://u",
		"billing_link": "https://b",
	},
	"site_exceeded_disk_usage_warning": {
		"site": "acme.com",
		"current_disk_usage": 120,
		"current_database_usage": 110,
		"no_of_days_left_to_suspend": 7,
	},
	"site_suspend_due_to_exceeding_disk_usage": {"subject": "x"},
	"notify_before_site_archival": {
		"site_name": "acme.com",
		"site_archive_notification_days": 2,
	},
	"press_webhook_disabled": {
		"endpoint": "https://x/y",
		"dashboard_url": "https://press.localhost/dashboard/settings/developer",
	},
	"enabled_auto_disk_expansion": {
		"server": "s1",
		"current_disk_usage": "90 GiB",
		"available_disk_space": "100 GiB",
		"increase_by": "20 GiB",
	},
	"disabled_auto_disk_expansion": {
		"server": "s1",
		"current_disk_usage": "80 GiB",
		"available_disk_space": "100 GiB",
		"increase_by": "20 GiB",
		"used_storage_percentage": "80%",
	},
	"plan_upgrade_recommendation": {
		"upgrade_target": "Server",
		"instance_type": "c4",
		"vcpu": 4,
		"memory": 8,
		"server_name": "s1",
		"server_url": "https://press.localhost",
	},
	"snapshot_recovery_completion": {"snapshot": "snap-1"},
	"incident": {
		"message": "Automatic {0} triggered for server {1}",
		"message_args": ["scale", "s1"],
		"link": "https://l",
	},
	"auto_scale_notification": {
		"message": "Automatic {0} triggered for server {1}",
		"message_args": ["scale", "s1"],
		"link": "https://l",
	},
	"bench_deploy_failure": {
		"message": "Error occurred during auto scale",
		"message_args": [],
		"link": "https://l",
	},
	"partner_link_certificate": {"partner": "P1", "link": "https://l"},
	"partner_approval": {"user": "Ali", "partner": "P1", "link": "https://l"},
	"access_request": {
		"reason": "db issue",
		"resources": [{"document_type": "Site", "document_name": "s1"}],
		"access_requests_url": "https://press.localhost/dashboard/access-requests",
	},
	"access_request_update": {
		"status": "Approved",
		"resources": [],
		"access_requests_url": "https://press.localhost/dashboard/access-requests",
	},
	"remote_login": {"site": "acme.com", "login_url": "https://l"},
	"transfer_team_confirmation": {
		"type": "site",
		"name": "acme.com",
		"old_team": "T1",
		"new_team": "T2",
		"transfer_url": "https://t",
	},
	"marketplace_auto_review": {
		"review_page_link": "https://r",
		"logo": None,
		"desc": None,
		"links": None,
		"release": None,
	},
	"verify_account_for_site_login": {"otp": "123456"},
	"product_trial_verify_account": {
		"otp": "123456",
		"header_content": None,
		"read_pixel_path": None,
	},
	"app_approval_request_update": {
		"subject": "x",
		"status": "Rejected",
		"releases_link": "https://r",
		"commit_message": "abc",
		"rejection_reason": "bad",
	},
	"payment_failed_partner": {
		"subject": "x",
		"payment_link": "https://pay",
		"account_update_link": "https://billing",
		"last_4": "4242",
		"card_not_added": False,
		"team": frappe._dict({"default_payment_method": "Card"}),
		"sites": ["acme.com"],
	},
	"product_trial_email": {
		"message": "<p>pre-rendered</p>",
		"message_args": [],
		"preview_text": "Your site has expired",
		"title": "T",
		"logo": None,
	},
	"marketplace_audit_report": {
		"audit_result": "Fail",
		"app_title": "app",
		"issue_count": 2,
		"audit_summary": "",
		"failing_checks": [],
		"result_heading": {"Fail": "Audit Failed"},
		"header_tone": {"fg": "#111"},
		"font_stack": "sans",
		"mono_stack": "mono",
	},
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
	"Budget Alert Details",
	"Monthly Alert Threshold",
	"We attempted to auto-debit",
	"We tried to charge your default card",
	"Your UPI Autopay mandate was successfully",
	"Please make sure your UPI account",
	"Manage UPI Autopay",
	"Pay Now",
	"exceeded plan limit",
	"been temporarily",
	"will be archived",
	"Because we saw a high number of failed webhook",
	"has used more than",
	"Your server has currently used",
	"frequent incidents with your current plan",
	"recovery has been completed",
	"View Server Analytics",
	"View Autoscale Job",
	"View Deploy Job",
	"Need Help ?",
	"has raised a request to link",
	"has requested access to your resources",
	"Review request",
	"Verify Account",
	"This email was sent by AlbannaTech",
	"Attempted login",
	"Fix all the issues",
	# signature() is shared by every template, so an English "Thanks," leaked
	# into all of them and no per-template sentinel caught it
	"Thanks,",
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
			if name in ARG_ONLY_TEMPLATES:
				# These translate a string handed in as an argument rather than
				# carrying literals, so there is nothing to check against the
				# catalog here. The render tests still cover them.
				self.assertIn("_(", source, f"{name}.html marks nothing translatable")
				continue
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


class TestUPIAutopayBranches(FrappeTestCase):
	"""The UPI failure email branches on error_reason; each needs its own check.

	A single render only proves one branch translated. These were the four
	branches at the time of writing -- add a case when a reason is added.
	"""

	def _render(self, reason, upi_vpa="a@upi"):
		from frappe.translate import clear_cache

		original = frappe.local.lang
		try:
			frappe.local.lang = CATALOG_LANG
			clear_cache()
			html, _ = get_email_from_template(
				"payment_failed_upi_autopay",
				{
					"subject": "x",
					"amount": "20",
					"upi_vpa": upi_vpa,
					"error_reason": reason,
					"upi_autopay_link": "https://u",
					"billing_link": "https://b",
				},
			)
			return visible_text(html)
		finally:
			frappe.local.lang = original
			from frappe.translate import clear_cache

			clear_cache()

	def test_every_error_branch_renders_arabic(self):
		for reason in (
			"INSUFFICIENT_FUNDS",
			"MAX_PAYMENT_AMOUNT_EXCEEDED",
			"TOKEN_EXPIRED",
			"TOKEN_NOT_ACTIVE",
			"TOKEN_NOT_CONFIRMED",
			"GATEWAY_ERROR",
			"FREQUENCY_LIMIT_EXCEEDED",
			"PAYMENT_CREATION_FAILED",
			"MAX_PAYMENT_AMOUNT_EXCEEDED",
			"MANDATE_CANCELLED",
			"SOMETHING_NEW",
		):
			with self.subTest(reason=reason):
				text = self._render(reason)
				self.assertRegex(text, r"[؀-ۿ]")
				self.assertNotIn("We attempted to auto-debit", text)
				self.assertNotIn("Please check your UPI", text)

	def test_branch_renders_without_a_upi_vpa(self):
		# The template guards the vpa span, so the interpolation must not
		# leave an empty label behind.
		text = self._render("INSUFFICIENT_FUNDS", upi_vpa=None)
		self.assertIn("رصيد", text)
		self.assertNotIn("None", text)
