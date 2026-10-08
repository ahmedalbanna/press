"""Measures how much of the outgoing email surface is actually translated.

Story 8 is only met when every customer email a user can receive has Arabic
copy. That is a content-completeness property, not a code property, so nothing
else in the suite notices when it is unmet: the plumbing passes, the email
renders, it just renders English.

This module reports the number and guards against it going backwards. The
threshold below is the floor as of this commit, not the target -- raise it as
templates land. For a launch where the language toggle is visible, it needs to
be at 100%, or the toggle should stay hidden.
"""

import ast
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

from press.tests.test_email_i18n import TRANSLATED_TEMPLATES

APP_ROOT = Path(frappe.get_app_path("press"))

# Floor for the share of sendmail templates carrying Arabic copy. Raise it as
# coverage improves; never lower it, that is how the number quietly regresses.
MIN_TRANSLATED_SHARE = 0.40


def _string_literals(node) -> list[str]:
	return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _templates_referenced_by_sendmail() -> set[str]:
	"""Every template name a sendmail call can send.

	Reads the literal and dict-arg forms; templates passed as a variable
	(`template=template`) are missed, so treat the result as a lower bound.
	"""
	found: set[str] = set()
	for path in sorted(APP_ROOT.rglob("*.py")):
		if "tests" in path.parts:
			continue
		try:
			tree = ast.parse(path.read_text())
		except SyntaxError:
			continue
		for node in ast.walk(tree):
			if not isinstance(node, ast.Call):
				continue
			name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
			if name not in ("sendmail", "send_user_email"):
				continue
			for kw in node.keywords:
				if kw.arg == "template":
					found.update(_string_literals(kw.value))
				elif kw.arg == "args":
					for inner in ast.walk(kw.value):
						if not isinstance(inner, ast.Dict):
							continue
						for k, v in zip(inner.keys, inner.values, strict=False):
							if isinstance(k, ast.Constant) and k.value == "template":
								found.update(_string_literals(v))
	return found


class TestEmailTranslationCoverage(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.referenced = _templates_referenced_by_sendmail()
		self.translated = set(TRANSLATED_TEMPLATES)

	def test_coverage_does_not_regress(self):
		if not self.referenced:
			self.skipTest("no sendmail template references found")
		share = len(self.referenced & self.translated) / len(self.referenced)
		self.assertGreaterEqual(
			share,
			MIN_TRANSLATED_SHARE,
			f"only {share:.0%} of {len(self.referenced)} sendmail templates are "
			f"translated (floor {MIN_TRANSLATED_SHARE:.0%}); untranslated: "
			f"{sorted(self.referenced - self.translated)}",
		)

	def test_translated_list_contains_no_dead_entries(self):
		# An entry naming a template nothing sends would inflate the number and
		# hide real gaps.
		orphans = {
			name
			for name in self.translated
			if not (APP_ROOT / "templates" / "emails" / f"{name}.html").exists()
		}
		self.assertEqual(orphans, set(), f"no such template: {orphans}")

	def test_every_listed_template_actually_marks_strings_translatable(self):
		empty = []
		for name in sorted(self.translated):
			source = (APP_ROOT / "templates" / "emails" / f"{name}.html").read_text()
			if "_(" not in source:
				empty.append(name)
		self.assertEqual(
			empty,
			[],
			f"listed as translated but mark nothing translatable: {empty}",
		)

	def test_reports_current_coverage(self):
		# Not an assertion: a number a human can read without running the suite
		# and decoding a diff.
		covered = sorted(self.referenced & self.translated)
		missing = sorted(self.referenced - self.translated)
		print(
			f"\nemail i18n coverage: {len(covered)}/{len(self.referenced)} "
			f"({len(covered) / max(len(self.referenced), 1):.0%})\n"
			f"  translated:   {', '.join(covered)}\n"
			f"  untranslated: {', '.join(missing)}"
		)
