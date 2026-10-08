"""RTL layout contract for the dashboard.

Tailwind v3 does not flip physical utilities when the document becomes
dir="rtl", so `dashboard/src/styles/rtl.css` re-declares the ones the dashboard
actually uses with their mirrored counterpart. That list is only correct while
someone keeps it in step with the sources, and nothing in a stylesheet can
enforce that on its own: a new `ml-3` would render on the wrong side in Arabic
and every functional test would still pass.

So these tests read the Vue/TS sources and compare. They fail when a
direction-sensitive utility appears without an RTL counterpart.

(An equivalent vitest spec would be the natural home for this, but the repo's
vitest is 0.9.x and cannot start against the installed vite plugins, so `yarn
test` fails before running anything. These live here because this suite runs.)
"""

import re
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase

DASHBOARD_SRC = Path(frappe.get_app_path("press")).parent / "dashboard" / "src"
RTL_CSS = DASHBOARD_SRC / "styles" / "rtl.css"
GLOBAL_CSS = DASHBOARD_SRC / "styles" / "global.css"
LANGUAGE_INDEX = DASHBOARD_SRC / "utils" / "language" / "index.ts"

SOURCE_SUFFIXES = (".vue", ".ts", ".js")

DIRECTIONAL_PATTERN = re.compile(
	r"\b((?:ml|mr|pl|pr|left|right|text-left|text-right|border-l|border-r"
	r"|rounded-l|rounded-r|inset-l|inset-r)-[0-9a-z./]+)\b"
)

# space-x-* is deliberately excluded. Its sibling margin is physical, but a
# dir="rtl" flex row already lays items out from the right, so mirroring it
# would double the gap rather than fix it.
NO_MIRROR_NEEDED = re.compile(r"^space-x-")


def _source_files(directory: Path):
	for path in sorted(directory.rglob("*")):
		if path.is_file() and path.suffix in SOURCE_SUFFIXES:
			yield path


def used_directional_classes() -> set[str]:
	found: set[str] = set()
	for path in _source_files(DASHBOARD_SRC):
		for match in DIRECTIONAL_PATTERN.finditer(path.read_text(encoding="utf-8")):
			found.add(match.group(1))
	return found


def _css_selector(class_name: str) -> str:
	"""The class as it appears in a built stylesheet.

	Tailwind escapes the dot in ml-0.5 to .ml-0\\.5 and the slash in left-1/2 to
	.left-1\\/2, so a plain re.escape finds neither.
	"""
	# Escape for CSS first -- the built stylesheet writes ml-0\.5 and
	# left-1\/2 with literal backslashes -- then for the regex, because the
	# backslash itself has to match.
	return re.escape(class_name.replace(".", r"\.").replace("/", r"\/"))


def _has_rule(css: str, class_name: str) -> bool:
	"""True when the CSS scopes a rule to the class under [dir="rtl"]."""
	return bool(re.search(r'\[dir="rtl"\]\s+\.' + _css_selector(class_name) + r"(?![\w-])", css))


class TestRtlStylesheet(FrappeTestCase):
	def test_rtl_stylesheet_exists_and_is_imported(self):
		self.assertTrue(RTL_CSS.exists(), f"{RTL_CSS} is missing")
		global_css = GLOBAL_CSS.read_text(encoding="utf-8")
		self.assertIn(
			"rtl.css", global_css, "rtl.css is never imported, so none of it applies"
		)

	def test_mirrors_every_direction_sensitive_utility_used_in_the_dashboard(self):
		css = RTL_CSS.read_text(encoding="utf-8")
		missing = sorted(
			name
			for name in used_directional_classes()
			if not NO_MIRROR_NEEDED.match(name) and not _has_rule(css, name)
		)
		self.assertEqual(
			missing,
			[],
			"used in the dashboard but with no [dir=\"rtl\"] counterpart, so they "
			f"render on the wrong side in Arabic: {missing}",
		)

	def test_scan_actually_finds_classes(self):
		# A pattern that silently matches nothing would make the test above
		# pass vacuously.
		self.assertGreater(
			len(used_directional_classes()), 20, "directional class scan found nothing"
		)

	def test_space_x_is_not_mirrored(self):
		# Documented in rtl.css: mirroring it would double the gap.
		css = RTL_CSS.read_text(encoding="utf-8")
		self.assertNotRegex(css, r'\[dir="rtl"\]\s+\.space-x-')

	def test_mirrors_direction_sensitive_icons(self):
		css = RTL_CSS.read_text(encoding="utf-8")
		for icon in ("chevron-right", "chevron-left", "arrow-right", "arrow-left"):
			self.assertIn(f"lucide-{icon}", css, f"lucide-{icon} is not mirrored")
		self.assertIn("scaleX(-1)", css)

	def test_keeps_monospace_content_left_to_right(self):
		# Code, log panes and shell output are not Arabic prose, and mirroring
		# their punctuation makes them unreadable.
		css = RTL_CSS.read_text(encoding="utf-8")
		self.assertRegex(
			css, r'\[dir="rtl"\][^{]*\.font-mono[^{]*\{[^}]*direction:\s*ltr'
		)

	def test_mirrored_rules_also_reset_the_original_side(self):
		# Setting only the mirrored property leaves the physical one from
		# Tailwind still applied, so e.g. .ml-2 keeps margin-left alongside the
		# new margin-right and the element ends up wider than intended.
		css = RTL_CSS.read_text(encoding="utf-8")
		for source, cleared in (
			("ml-2", "margin-left: 0"),
			("ml-auto", "margin-left: 0"),
			("pl-2", "padding-left: 0"),
			("pr-2", "padding-right: 0"),
			("left-0", "left: auto"),
			("right-0", "right: auto"),
		):
			pattern = re.compile(
				r'\[dir="rtl"\]\s+\.' + _css_selector(source) + r"\s*\{([^}]*)\}"
			)
			match = pattern.search(css)
			self.assertIsNotNone(match, f".{source} has no RTL rule")
			self.assertIn(
				cleared,
				match.group(1),
				f".{source} mirrors its side but never clears the original "
				f"({cleared}); Tailwind's physical rule still applies underneath",
			)


class TestRtlActivation(FrappeTestCase):
	def test_language_switch_sets_dir_so_the_rtl_layer_applies(self):
		source = LANGUAGE_INDEX.read_text(encoding="utf-8")
		self.assertIn("document.documentElement.dir", source)
		self.assertRegex(source, r"dir\s*=\s*[^;\n]*rtl")

	def test_arabic_font_is_applied_at_the_document_level(self):
		css = GLOBAL_CSS.read_text(encoding="utf-8")
		self.assertIn('[dir="rtl"]', css)
		self.assertIn("Cairo", css)
