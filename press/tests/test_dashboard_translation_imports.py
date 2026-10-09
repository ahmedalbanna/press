"""Catches t() calls that never imported t.

The dashboard calls its translation helper as a bare `t('...')`. If the import
is missing the call throws a ReferenceError when the module is evaluated, which
the bundler does not catch -- `yarn build` passes, and nothing else in this
suite loads the SPA, so the dashboard only breaks when a user navigates to the
affected page. Seven files were in that state, one of them the router's access
requests view.

A module-scope `t(...)` inside an object literal is the shape that fails most
often, because it runs at import time rather than on render.
"""

import re
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

SRC = Path(frappe.get_app_path("press")).parent / "dashboard" / "src"
SOURCE_SUFFIXES = (".ts", ".js", ".vue")

# t( as a bare call: not $t, not .t(, not part of a longer identifier
T_CALL = re.compile(r"(?<![\w$.])t\(\s*[\"']")
# a named import of t from any language module
T_IMPORT = re.compile(
	r"import\s*\{[^}]*\bt\b[^}]*\}\s*from\s*['\"][^'\"]*language[^'\"]*['\"]"
)


def _files():
	for path in sorted(SRC.rglob("*")):
		if path.is_file() and path.suffix in SOURCE_SUFFIXES:
			yield path


class TestTranslationImports(FrappeTestCase):
	def test_every_file_calling_t_imports_it(self):
		missing = []
		for path in _files():
			source = path.read_text(encoding="utf-8", errors="replace")
			if not T_CALL.search(source):
				continue
			if not T_IMPORT.search(source):
				missing.append(path.relative_to(SRC).as_posix())
		self.assertEqual(
			missing,
			[],
			"these call t() without importing it, so they throw a ReferenceError "
			f"as soon as the module loads: {missing}",
		)

	def test_the_translation_helper_is_actually_exported(self):
		# Guards against the import existing but the name drifting, which would
		# trade a missing import for an undefined one.
		module = SRC / "utils" / "language" / "index.ts"
		source = module.read_text(encoding="utf-8")
		self.assertRegex(source, r"export\s+function\s+t\b")
		self.assertRegex(source, r"export\s+default\s*\{")

	def test_the_scan_is_not_vacuously_passing(self):
		# If the call pattern stopped matching, the test above would pass
		# having checked nothing.
		callers = [
			path
			for path in _files()
			if T_CALL.search(path.read_text(encoding="utf-8", errors="replace"))
		]
		self.assertGreater(
			len(callers), 50, f"only {len(callers)} files call t(); pattern is suspect"
		)
