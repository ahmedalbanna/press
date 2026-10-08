"""Keeps press/translations/ar.csv in step with the dashboard dictionaries.

Frappe resolves _() inside an email template through the app's translation
catalog, while the SPA reads the TypeScript dictionaries. The catalog used to be
maintained by hand alongside them, so the same English string could carry
different Arabic depending on which surface rendered it -- eight did.

dashboard/scripts/generate-translations.mjs now emits the catalog from the
dictionaries and yarn build runs it first. The output is committed as well as
generated, because Frappe needs it present on a fresh checkout, which leaves the
two free to drift. This closes that gap.
"""

import csv
import json
import subprocess
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

APP_ROOT = Path(frappe.get_app_path("press"))
DASHBOARD = APP_ROOT.parent / "dashboard"
GENERATOR = DASHBOARD / "scripts" / "generate-translations.mjs"
CATALOG = APP_ROOT / "translations" / "ar.csv"
DICT_DIR = DASHBOARD / "src" / "utils" / "language"


def read_catalog() -> dict[str, str]:
	with CATALOG.open(encoding="utf-8", newline="") as handle:
		return {row[0]: row[1] for row in csv.reader(handle) if len(row) == 2 and row[0]}


def run_generator() -> subprocess.CompletedProcess:
	return subprocess.run(
		["node", str(GENERATOR)],
		cwd=str(DASHBOARD),
		capture_output=True,
		text=True,
		timeout=180,
	)


class TestTranslationCatalogIsGenerated(FrappeTestCase):
	def test_generator_exists_and_is_wired_into_the_build(self):
		self.assertTrue(GENERATOR.exists(), f"{GENERATOR} is missing")
		scripts = json.loads((APP_ROOT.parent / "package.json").read_text())["scripts"]
		self.assertIn("generate-translations", scripts)
		# Ahead of the CSS builds, which are what consume the catalog.
		self.assertLess(
			scripts["build-all"].index("generate-translations"),
			scripts["build-all"].index("build-email-css"),
			"the catalog must be generated before the email CSS build",
		)

	def test_committed_catalog_matches_the_dictionaries(self):
		# Run the generator into a scratch copy and compare, rather than letting
		# it overwrite the committed file -- a failing check should leave the
		# repo as it was.
		before = CATALOG.read_bytes()
		result = run_generator()
		self.assertEqual(
			result.returncode,
			0,
			f"generator failed:\n{result.stdout}\n{result.stderr}",
		)
		after = CATALOG.read_bytes()
		self.assertEqual(
			before,
			after,
			"press/translations/ar.csv is out of date. Run "
			"`yarn generate-translations` (or `node dashboard/scripts/"
			"generate-translations.mjs`) and commit the result.",
		)

	def test_catalog_uses_lf_line_endings(self):
		# csv.writer defaults to CRLF, which shows up as a whole-file diff in
		# review and is inconsistent with the rest of the repo.
		self.assertNotIn(b"\r\n", CATALOG.read_bytes())

	def test_every_dictionary_entry_reaches_the_catalog(self):
		generated = read_catalog()
		committed = read_catalog()
		self.assertGreater(len(generated), 1000)
		missing = set(generated) - set(committed)
		self.assertEqual(missing, set(), f"catalog is missing: {sorted(missing)[:5]}")

	def test_catalog_has_no_duplicate_source_strings(self):
		with CATALOG.open(encoding="utf-8", newline="") as handle:
			keys = [row[0] for row in csv.reader(handle) if row]
		duplicates = {key for key in keys if keys.count(key) > 1}
		self.assertEqual(
			duplicates, set(), f"duplicate catalog keys: {sorted(duplicates)[:5]}"
		)

	def test_untranslated_entries_are_declared_not_accidental(self):
		# A handful of identifiers stay in Latin on purpose. Anything else whose
		# Arabic equals its English is a forgotten translation, so it is named
		# explicitly and reviewed rather than inferred.
		catalog = read_catalog()
		by_choice = {"API Key", "API Secret", "SSH", "JSON", "Webhook", "Frappe Partner"}
		accidental = {
			key
			for key, value in catalog.items()
			if value == key and key not in by_choice
		}
		self.assertEqual(
			accidental,
			set(),
			f"these resolve to English and were never translated: {sorted(accidental)[:10]}",
		)
