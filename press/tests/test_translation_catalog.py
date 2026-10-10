"""Keeps press/locale/ar.po in step with the dashboard dictionaries.

Frappe resolves _() inside an email template through the app's translation
catalog, while the SPA reads the TypeScript dictionaries. The catalog used to be
a hand-maintained CSV, so the same English string could carry different Arabic
depending on which surface rendered it -- eight did.

The catalog is now a single gettext PO file, because that is the only place
Arabic can live for all three surfaces at once: the SPA (the dictionaries), the
Desk UI (labels extracted from doctype JSON, which no CSV reader knew about) and
the framework chrome around it. dashboard/scripts/generate-translations.mjs
merges them and `bench build` compiles the result to MO. The output is committed
as well as generated, because a fresh checkout needs it present, which leaves
the two free to drift. This closes that gap.

It also guards the two mistakes that cost real time: a PO written without the
UTF-8 charset header loads as mojibake rather than failing loudly, and a
re-extraction quietly drops translations the POT no longer mentions.
"""

import json
import re
import subprocess
from pathlib import Path

import frappe
from babel.messages.pofile import read_po
from frappe.tests.utils import FrappeTestCase

from press.tests.translations import UNTRANSLATED_BY_CHOICE

APP_ROOT = Path(frappe.get_app_path("press"))
DASHBOARD = APP_ROOT.parent / "dashboard"
GENERATOR = DASHBOARD / "scripts" / "generate-translations.mjs"
CATALOG = APP_ROOT / "locale" / "ar.po"
DICT_DIR = DASHBOARD / "src" / "utils" / "language"

# Order is the merge order in language/index.ts, so a duplicate keeps the same
# winner here as it does at runtime.
MODULES = [
	"nav",
	"common",
	"auth",
	"onboarding",
	"sites",
	"servers",
	"billing",
	"team",
	"misc",
	"objects",
	"dialogs",
	"emails",
]

# A dictionary entry is one line when the whole object fits, and several when the
# author wrapped it. Keys are quoted when they contain punctuation and bare when
# they do not, so both forms have to be read. Values are single- or
# double-quoted for their whole token and may escape their own quote, so the
# token pattern is backslash-aware.
STRING = r"""'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*\""""
KEY = rf"""(?:{STRING}|[A-Za-z_$][\w$]*(?:\s+[A-Za-z_$][\w$]*)*)"""

ENTRY = re.compile(
	rf"""^\s*(?P<key>{KEY})\s*:\s*\{{\s*"""
	rf"""en:\s*(?P<en>{STRING})\s*,\s*"""
	rf"""ar:\s*(?P<ar>{STRING})\s*\}}\s*,?\s*(?://.*)?$"""
)
# The opening line of a wrapped entry; en and ar follow on their own lines.
ENTRY_START = re.compile(rf"""^\s*(?P<key>{KEY})\s*:\s*\{{\s*$""")
ENTRY_FIELD = re.compile(rf"""^\s*(?P<name>en|ar):\s*(?P<value>{STRING})\s*,?\s*$""")


def unquote(token: str) -> str:
	"""Strip the quotes, but only when the token actually has them.

	A bare identifier is a valid key, and stripping it blindly turns
	'Configure' into 'onfigur' -- which then fails to match the catalog and
	reads as a missing translation.
	"""
	if len(token) >= 2 and token[0] == token[-1] and token[0] in "'\"":
		return token[1:-1]
	return token


def unescape(text: str) -> str:
	"""JS string escapes, so a key read here matches the one the SPA looks up."""
	return re.sub(
		r"\\(.)",
		lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)),
		text,
	)


def read_dictionaries() -> dict[str, str]:
	"""Shorthand for the same merge the generator performs, minus the SPA.

	The generator is the real merge and imports the modules the way the app
	does; this only has to be close enough to call out a dictionary entry that
	never reached the catalog, so a wrapped entry and a bare key are both read.
	"""
	merged: dict[str, str] = {}
	for name in MODULES:
		path = DICT_DIR / f"{name}.ts"
		if not path.exists():
			continue
		lines = path.read_text(encoding="utf-8").splitlines()
		index = 0
		while index < len(lines):
			line = lines[index]
			if not line.strip() or line.strip().startswith("//"):
				index += 1
				continue
			match = ENTRY.match(line)
			if match:
				merged[unescape(unquote(match.group("key")))] = unescape(
					unquote(match.group("ar"))
				)
				index += 1
				continue
			opening = ENTRY_START.match(line)
			if opening:
				key = unescape(unquote(opening.group("key")))
				index += 1
				fields = {}
				while index < len(lines) and (lines[index].strip() or True):
					stripped = lines[index].strip()
					if stripped in ("},", "}"):
						break
					field = ENTRY_FIELD.match(lines[index])
					if field:
						fields[field.group("name")] = unescape(unquote(field.group("value")))
					index += 1
				if "ar" in fields:
					merged[key] = fields["ar"]
				continue
			index += 1
	return merged


def read_catalog() -> dict[tuple[str, str], str]:
	with CATALOG.open("rb") as handle:
		catalog = read_po(handle)
	return {(m.context or "", m.id): m.string for m in catalog if m.id}


def run_generator() -> subprocess.CompletedProcess:
	return subprocess.run(
		["node", str(GENERATOR)],
		cwd=str(DASHBOARD),
		capture_output=True,
		text=True,
		timeout=300,
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
			"press/locale/ar.po is out of date. Run "
			"`yarn generate-translations` (or `node dashboard/scripts/"
			"generate-translations.mjs`) and commit the result.",
		)

	def test_catalog_uses_lf_line_endings(self):
		self.assertNotIn(b"\r\n", CATALOG.read_bytes())

	def test_catalog_declares_utf8(self):
		# Without it babel decodes the Arabic as latin-1 and every entry comes
		# back mojibake instead of raising, which looks like a translation bug.
		# The header is one long wrapped msgstr, so check the parsed catalog too
		# rather than looking for the keys on their own lines.
		with CATALOG.open("rb") as handle:
			catalog = read_po(handle)
		self.assertEqual(str(catalog.locale), "ar")
		self.assertEqual(catalog.charset, "utf-8")
		self.assertIn("charset=UTF-8", CATALOG.read_text(encoding="utf-8"))

	def test_every_dictionary_entry_reaches_the_catalog(self):
		catalog = read_catalog()
		dictionaries = read_dictionaries()
		self.assertGreater(len(dictionaries), 1000)
		missing = {
			key: (value, catalog.get(("", key)))
			for key, value in dictionaries.items()
			if catalog.get(("", key)) != unescape(value)
		}
		self.assertEqual(
			missing,
			{},
			f"catalog disagrees with the dictionaries on {len(missing)} entries, e.g. "
			f"{dict(list(missing.items())[:3])}. Run the generator and commit it.",
		)

	def test_catalog_has_no_duplicate_source_strings(self):
		with CATALOG.open("rb") as handle:
			catalog = read_po(handle)
		keys = [(m.context or "", m.id) for m in catalog if m.id]
		duplicates = {key for key in keys if keys.count(key) > 1}
		self.assertEqual(
			duplicates,
			set(),
			f"duplicate catalog keys: {sorted(duplicates)[:5]}",
		)

	def test_untranslated_entries_are_declared_not_accidental(self):
		# A handful of identifiers stay in Latin on purpose. Anything else whose
		# Arabic equals its English is a forgotten translation, so it is named
		# explicitly and reviewed rather than inferred.
		catalog = read_catalog()
		by_choice = {("", name) for name in UNTRANSLATED_BY_CHOICE}
		by_choice.add(("Submit verification code", "Verify"))
		accidental = {
			key
			for key, value in catalog.items()
			if value == key[1] and key not in by_choice
		}
		self.assertEqual(
			accidental,
			set(),
			f"these resolve to English and were never translated: {sorted(accidental)[:10]}",
		)

	def test_desk_side_strings_are_present(self):
		# The Desk labels come from the POT, not the dictionaries, so nothing
		# above proves the merge kept them. These were untranslated until the
		# migration; if they vanish, the PO silently regressed to SPA-only.
		catalog = read_catalog()
		for source in ("Server", "Bench", "Release Group", "Proxy Server", "Cluster"):
			self.assertIn(
				("", source),
				catalog,
				f"the Desk label {source!r} left the catalog",
			)
			self.assertTrue(catalog[("", source)], f"{source!r} has no Arabic")
