"""Guards the AlbannaTech white-label contract.

The spec's Testing Decisions named five surfaces; this module covers all five.
They assert on file contents and app metadata rather than rendering through a
browser, because what regresses here is a brand string or a token getting
overwritten by an upstream merge -- not behaviour.
"""

from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

from press import hooks

APP_ROOT = Path(frappe.get_app_path("press"))

BRAND_COLORS = {
	"primary": "#0F172A",
	"secondary": "#0EA5E9",
	"accent": "#10B981",
	"bg-light": "#F8FAFC",
	"bg-dark": "#020617",
}


class TestAppMetadata(FrappeTestCase):
	"""Spec: hooks.py must carry AlbannaTech's identity."""

	def test_app_title_and_publisher_are_albannatech(self):
		self.assertEqual(hooks.app_title, "AlbannaTech")
		self.assertEqual(hooks.app_publisher, "AlbannaTech")

	def test_app_description_names_erpnext_not_frappe(self):
		self.assertEqual(hooks.app_description, "Managed ERPNext Hosting")

	def test_app_email_is_the_albannatech_support_address(self):
		self.assertEqual(hooks.app_email, "support@albannatech.com")

	def test_app_color_is_a_brand_hex_not_a_frappe_ui_colour_name(self):
		# Frappe UI preset names ("grey") do not render as the AlbannaTech navy.
		self.assertEqual(hooks.app_color, BRAND_COLORS["secondary"])


class TestDashboardEntryPoint(FrappeTestCase):
	"""Spec: dashboard/index.html carries the title, favicon and font links."""

	def setUp(self):
		super().setUp()
		self.html = (APP_ROOT.parent / "dashboard" / "index.html").read_text()

	def test_title_is_albannatech_not_frappe_cloud(self):
		self.assertIn("<title>AlbannaTech</title>", self.html)
		self.assertNotIn("<title>Frappe Cloud</title>", self.html)

	def test_favicon_is_served_from_the_dashboard_public_dir(self):
		# Vite only serves /favicon.svg from dashboard/public; an
		# /assets/press/... path fails to resolve at build time.
		self.assertIn('href="/favicon.svg"', self.html)

	def test_google_fonts_stylesheet_is_present_not_just_preconnect(self):
		self.assertIn("fonts.googleapis.com/css2", self.html)
		for family in ("Cairo", "Inter", "Plus+Jakarta+Sans"):
			self.assertIn(family, self.html)


class TestBrandAssetTokens(FrappeTestCase):
	"""Spec: brand colours are declared as CSS custom properties."""

	def _assert_tokens(self, css: str, label: str) -> None:
		for name, value in BRAND_COLORS.items():
			self.assertIn(
				f"--brand-{name}: {value}",
				css,
				f"{label} is missing --brand-{name}",
			)

	def test_dashboard_global_css_defines_every_brand_token(self):
		css = (APP_ROOT.parent / "dashboard" / "src" / "styles" / "global.css").read_text()
		self._assert_tokens(css, "global.css")

	def test_marketplace_css_defines_every_brand_token(self):
		css = (APP_ROOT / "public" / "css" / "marketplace-next.css").read_text()
		self._assert_tokens(css, "marketplace-next.css")

	def test_saas_css_defines_every_brand_token(self):
		css = (APP_ROOT / "public" / "css" / "saas-next.css").read_text()
		self._assert_tokens(css, "saas-next.css")

	def test_no_duplicate_token_declarations_across_dashboard_stylesheets(self):
		# A dead second token file used to shadow these under --primary/--secondary.
		assets = APP_ROOT.parent / "dashboard" / "src" / "assets"
		self.assertFalse(
			(assets / "style.css").exists(),
			"assets/style.css duplicates the live brand tokens and drifts from them",
		)


class TestBrandedTemplates(FrappeTestCase):
	"""Spec: signup, login, marketplace and email templates are AlbannaTech's."""

	def test_login_box_renders_the_albannatech_logo_not_the_frappe_cloud_mark(self):
		component = (
			APP_ROOT.parent
			/ "dashboard"
			/ "src"
			/ "components"
			/ "auth"
			/ "LoginBox.vue"
		).read_text()
		self.assertIn("/albannatech-logo.svg", component)
		self.assertNotIn("FCLogo", component)

	def test_saas_login_box_renders_the_albannatech_logo(self):
		component = (
			APP_ROOT.parent
			/ "dashboard"
			/ "src"
			/ "components"
			/ "auth"
			/ "SaaSLoginBox.vue"
		).read_text()
		self.assertIn("/albannatech-logo.svg", component)
		self.assertNotIn("FCLogo", component)

	def test_no_dashboard_component_still_renders_the_frappe_cloud_logo(self):
		src = APP_ROOT.parent / "dashboard" / "src"
		offenders = [
			path.relative_to(src).as_posix()
			for path in src.rglob("*.vue")
			if "FCLogo" in path.read_text()
		]
		self.assertEqual(offenders, [], f"still rendering Frappe Cloud mark: {offenders}")

	def test_email_base_template_defaults_to_albannatech(self):
		base = (APP_ROOT / "templates" / "emails" / "base.html").read_text()
		self.assertIn("AlbannaTech", base)
		self.assertNotIn("Frappe Cloud", base)

	def test_marketplace_page_title_is_albannatech(self):
		base = (APP_ROOT / "templates" / "marketplace" / "base.html").read_text()
		self.assertIn("AlbannaTech Marketplace", base)
		self.assertNotIn("Frappe Cloud Marketplace", base)


class TestSupportLinkSweep(FrappeTestCase):
	"""Spec: no frappecloud.com / frappe.io / erpnext.com links on customer surfaces.

	docs.frappe.io is deliberately excluded -- those are upstream Frappe Cloud
	product docs, and AlbannaTech has no docs site of its own to point at yet.
	Rewriting them would trade a working link for a 404.
	"""

	REWRITABLE = ("frappecloud.com", "support.frappe.io", "erpnext.com")

	def _customer_facing_templates(self):
		for sub in ("emails", "saas"):
			yield from (APP_ROOT / "templates" / sub).glob("*.html")

	def test_no_customer_facing_template_still_links_to_frappe_or_erpnext(self):
		offenders = []
		for path in self._customer_facing_templates():
			text = path.read_text()
			for host in self.REWRITABLE:
				if host in text:
					offenders.append(f"{path.name}: {host}")
		self.assertEqual(offenders, [], f"unrewritten host references: {offenders}")

	def test_emails_route_support_requests_to_the_albannatech_address(self):
		offenders = [
			path.name
			for path in (APP_ROOT / "templates" / "emails").glob("*.html")
			if "support.frappe.io" in path.read_text()
		]
		self.assertEqual(
			offenders,
			[],
			f"emails still send customers to the Frappe helpdesk: {offenders}",
		)