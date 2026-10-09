"""Translation plumbing contract for the dashboard.

The helpers `t()`/`tr()` are registered as Vue globals in `main.js`, so every
template in the app -- Options API or `<script setup>` -- can call them with
no import and no `methods` entry. Only bare calls in `<script>` scope need an
import from `@/utils/language`.

These tests enforce that contract from both sides: script scope must import
what it calls, and the globals the templates rely on must stay registered in
`main.js`. Neither the bundler nor anything else in this suite loads the SPA,
so without them a missing import is a blank page discovered by a user, not a
red build. Seven files were once in that state, one of them the router's
access requests view.
"""

import re
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

SRC = Path(frappe.get_app_path("press")).parent / "dashboard" / "src"
MAIN_JS = SRC / "main.js"

# t( or tr( as a bare call: not $t, not .t(, not part of a longer identifier
T_CALL = re.compile(r"(?<![\w$.])(t|tr)\(\s*[\"']")
# a named import of t/tr from any language module
T_IMPORT = re.compile(
	r"import\s*\{([^}]*)\}\s*from\s*['\"][^'\"]*language[^'\"]*['\"]"
)


def _imported_helpers(source):
	match = T_IMPORT.search(source)
	if not match:
		return set()
	return set(re.findall(r"[A-Za-z_$][\w$]*", match.group(1)))


def _script_of(source):
	"""The <script> block of a .vue file, or the whole file for .ts/.js."""
	match = re.search(r"<script(?![^>]*setup)[^>]*>(.*?)</script>", source, re.S)
	if match:
		return match.group(1)
	match = re.search(r"<script setup[^>]*>(.*?)</script>", source, re.S)
	return match.group(1) if match else source


def _vue_files():
	return sorted(SRC.rglob("*.vue"))


def _script_files():
	return [p for p in sorted(SRC.rglob("*")) if p.suffix in (".ts", ".js")]


def _registered_globals():
	"""Helpers main.js exposes to every template via globalProperties."""
	main = MAIN_JS.read_text(encoding="utf-8")
	return set(re.findall(r"globalProperties\.(t|tr)\b", main))


class TestTranslationImports(FrappeTestCase):
	def test_script_scope_imports_what_it_calls(self):
		# Templates resolve t()/tr() through the main.js globals, but a bare
		# call in <script> scope has no such fallback and throws.
		missing = []
		for path in _vue_files():
			source = path.read_text(encoding="utf-8", errors="replace")
			called = set(T_CALL.findall(_script_of(source)))
			if called and not (called & _imported_helpers(source)):
				missing.append(path.relative_to(SRC).as_posix())
		for path in _script_files():
			source = path.read_text(encoding="utf-8", errors="replace")
			called = set(T_CALL.findall(source))
			if called and not (called & _imported_helpers(source)):
				missing.append(path.relative_to(SRC).as_posix())
		self.assertEqual(
			missing,
			[],
			"these call t()/tr() in <script> scope without importing it, so "
			f"they throw a ReferenceError as soon as the module loads: {missing}",
		)

	def test_templates_only_rely_on_registered_globals(self):
		# A template may skip the import only because main.js registers the
		# helper globally. If that line is ever deleted, every such template
		# breaks at render.
		registered = _registered_globals()
		unregistered = []
		for path in _vue_files():
			source = path.read_text(encoding="utf-8", errors="replace")
			template = re.search(r"<template>(.*?)</template>", source, re.S)
			if not template:
				continue
			for name in sorted(set(T_CALL.findall(template.group(1)))):
				if name not in registered:
					unregistered.append(
						f"{path.relative_to(SRC).as_posix()} -> {name}()"
					)
		self.assertEqual(
			unregistered,
			[],
			"these templates call a helper main.js never registered globally, "
			f"so they throw at render: {unregistered}",
		)

	def test_the_translation_helpers_are_actually_exported(self):
		# Guards against the import existing but the name drifting, which would
		# trade a missing import for an undefined one.
		module = SRC / "utils" / "language" / "index.ts"
		source = module.read_text(encoding="utf-8")
		self.assertRegex(source, r"export\s+function\s+t\b")
		self.assertRegex(source, r"export\s+function\s+tr\b")

	def test_the_scan_is_not_vacuously_passing(self):
		# If the call pattern stopped matching, the tests above would pass
		# having checked nothing.
		callers = [
			path
			for path in _vue_files()
			if T_CALL.search(path.read_text(encoding="utf-8", errors="replace"))
		]
		self.assertGreater(
			len(callers), 50, f"only {len(callers)} files call t(); pattern is suspect"
		)
