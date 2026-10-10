# Copyright (c) 2026, AlbannaTech and contributors
# For license information, please see license.txt

"""Language and theme registries plus the per-user preference that points at them.

`Language` and `Theme` are doctypes so the offered languages and the colour
tokens behind each theme are editable from Desk. `Account Settings` is the
one-row-per-user preference referencing them. The dictionaries still own the
translated words and the stylesheet still owns the layout; these records only
say which languages exist and what a theme's colours are.
"""

import frappe

from press.press.doctype.press_language.press_language import get_default_language
from press.press.doctype.press_theme.press_theme import get_default_theme

# Offered on a fresh install. Enabling a language makes it selectable; it does
# not create its messages, which still ship in press/translations/.
LANGUAGES = [
	{
		"language_code": "en",
		"language_name": "English",
		"english_name": "English",
		"direction": "ltr",
		"is_default": 1,
	},
	{
		"language_code": "ar",
		"language_name": "العربية",
		"english_name": "Arabic",
		"direction": "rtl",
		"is_default": 0,
	},
]

# Baseline colours, mirroring dashboard/src/styles/global.css. The drift test
# press.press.doctype.theme.test_theme_theme asserts the two stay equal.
LIGHT_THEME_TOKENS = {
	"brand-primary": "#0F172A",
	"brand-secondary": "#0EA5E9",
	"brand-accent": "#10B981",
	"brand-bg-light": "#F8FAFC",
	"brand-bg-dark": "#020617",
	"surface-blue-3": "#0284c7",
	"surface-gray-1": "#f8fafc",
	"surface-gray-2": "#f1f5f9",
	"surface-gray-3": "#e2e8f0",
	"surface-gray-4": "#cbd5e1",
	"surface-gray-5": "#94a3b8",
	"surface-blue-1": "#f0f9ff",
	"surface-blue-2": "#e0f2fe",
	"surface-green-2": "#ecfdf5",
	"surface-green-3": "#10b981",
	"surface-red-5": "#dc2626",
	"surface-modal": "#ffffff",
	"outline-gray-1": "#e2e8f0",
	"outline-gray-2": "#cbd5e1",
	"outline-gray-3": "#94a3b8",
	"outline-gray-4": "#64748b",
	"outline-gray-modals": "#e2e8f0",
	"outline-blue-1": "#0ea5e9",
	"ink-gray-9": "#0f172a",
	"ink-gray-8": "#1e293b",
	"ink-gray-7": "#475569",
	"ink-gray-6": "#64748b",
	"ink-gray-5": "#94a3b8",
	"ink-gray-4": "#94a3b8",
	"ink-gray-3": "#cbd5e1",
	"ink-gray-1": "#0f172a",
	"ink-white": "#ffffff",
	"scrollbar-thumb": "var(--surface-gray-4)",
	"scrollbar-thumb-hover": "var(--surface-gray-5)",
	"scrollbar-bg": "transparent",
	"scrollbar-size": "4px",
}

DARK_THEME_TOKENS = {
	"surface-white": "#0f172a",
	"surface-cards": "#1e293b",
	"surface-modal": "#1e293b",
	"surface-menu-bar": "#020617",
	"surface-selected": "#334155",
	"surface-gray-1": "#1e293b",
	"surface-gray-2": "#334155",
	"surface-gray-3": "#475569",
	"surface-gray-4": "#64748b",
	"surface-gray-5": "#94a3b8",
	"surface-blue-1": "#1e3a5f",
	"surface-blue-2": "#1d4ed8",
	"surface-green-2": "#065f46",
	"surface-red-2": "#451a1a",
	"outline-white": "#1e293b",
	"outline-gray-1": "#334155",
	"outline-gray-2": "#475569",
	"outline-gray-3": "#64748b",
	"outline-gray-modals": "#334155",
	"outline-blue-1": "#1e3a5f",
	"ink-gray-9": "#f8fafc",
	"ink-gray-8": "#e2e8f0",
	"ink-gray-7": "#cbd5e1",
	"ink-gray-6": "#94a3b8",
	"ink-gray-5": "#94a3b8",
	"ink-gray-4": "#64748b",
	"ink-gray-3": "#475569",
	"ink-gray-1": "#cbd5e1",
	"ink-white": "#020617",
	"scrollbar-thumb": "var(--surface-gray-2)",
	"scrollbar-thumb-hover": "var(--surface-gray-3)",
}

THEMES = [
	{"theme_name": "light", "label": "Light", "is_default": 1, "tokens": LIGHT_THEME_TOKENS},
	{"theme_name": "dark", "label": "Dark", "is_default": 0, "tokens": DARK_THEME_TOKENS},
]


def ensure_default_languages_and_themes():
	"""Seed Press Language, Press Theme and Press Account Settings rows.

	Safe to re-run: existing rows are left as an admin left them, so a tuned
	token or a moved default is never overwritten.
	"""
	for language in LANGUAGES:
		_insert_if_missing("Press Language", language["language_code"], {**language, "enabled": 1})

	for theme in THEMES:
		_insert_if_missing(
			"Press Theme",
			theme["theme_name"],
			{
				"theme_name": theme["theme_name"],
				"label": theme["label"],
				"is_default": theme["is_default"],
				"enabled": 1,
				"tokens": [
					{"token_name": name, "token_value": value} for name, value in theme["tokens"].items()
				],
			},
		)

	backfill_account_settings()


def _insert_if_missing(doctype: str, name: str, values: dict):
	if frappe.db.exists(doctype, name):
		return
	frappe.get_doc({"doctype": doctype, **values}).insert(ignore_if_duplicate=True)


def backfill_account_settings():
	"""Give every user a preference row, adopting their existing language.

	An existing install already stores the language on `User.language`, so that
	value is carried over instead of reset to the default.
	"""
	default_language = get_default_language()
	for user in frappe.get_all("User", filters={"enabled": 1}, pluck="name"):
		if frappe.db.exists("Press Account Settings", user):
			continue

		language = frappe.db.get_value("User", user, "language") or default_language
		if not frappe.db.exists("Press Language", language):
			language = default_language

		frappe.get_doc(
			{
				"doctype": "Press Account Settings",
				"user": user,
				"language": language,
				"theme": get_default_theme(),
			}
		).insert(ignore_permissions=True, ignore_if_duplicate=True)


def get_languages() -> list[dict]:
	"""Enabled languages, for the dashboard's language picker."""
	return frappe.get_all(
		"Press Language",
		filters={"enabled": 1},
		fields=["language_code", "language_name", "english_name", "direction"],
		order_by="is_default desc, language_name asc",
	)


def get_themes() -> list[dict]:
	"""Enabled themes with their tokens, for the dashboard to apply."""
	themes = frappe.get_all(
		"Press Theme",
		filters={"enabled": 1},
		fields=["theme_name", "label"],
		order_by="is_default desc, label asc",
	)
	for theme in themes:
		theme["tokens"] = get_theme_tokens(theme["theme_name"])
	return themes


def get_theme_tokens(theme_name: str) -> dict:
	"""Token name to value for one theme."""
	tokens = frappe.get_all(
		"Press Theme Token",
		filters={"parent": theme_name},
		fields=["token_name", "token_value"],
		order_by="idx",
	)
	return {token["token_name"]: token["token_value"] for token in tokens}


def get_account_settings(user: str | None = None) -> dict:
	"""The user's language, theme and text direction."""
	user = user or frappe.session.user
	preference = (
		frappe.db.get_value("Press Account Settings", user, ["language", "theme"], as_dict=True)
		or frappe._dict()
	)

	language = _resolve("Press Language", preference.language, get_default_language())
	return frappe._dict(
		{
			"language": language,
			"theme": _resolve("Press Theme", preference.theme, get_default_theme()),
			"direction": frappe.db.get_value("Press Language", language, "direction") or "ltr",
		}
	)


def _resolve(doctype: str, value: str | None, fallback: str) -> str:
	if value and frappe.db.exists(doctype, value):
		return value
	return fallback


def set_language(language: str) -> dict:
	"""Point the user at a language, keeping `User.language` in step.

	`User.language` stays authoritative for server-side translation of emails,
	so it is written here too.
	"""
	language = (language or "").strip().lower()
	_assert_selectable("Press Language", language)
	_save_setting("language", language)
	frappe.db.set_value("User", frappe.session.user, "language", language)
	return get_account_settings()


def set_theme(theme: str) -> dict:
	"""Point the user at a theme."""
	theme = (theme or "").strip().lower()
	_assert_selectable("Press Theme", theme)
	_save_setting("theme", theme)
	return get_account_settings()


def _assert_selectable(doctype: str, name: str):
	if not frappe.db.exists(doctype, name):
		frappe.throw(f"{doctype} {name!r} does not exist.")
	if not frappe.db.get_value(doctype, name, "enabled"):
		frappe.throw(f"{doctype} {name!r} is disabled.")


def _save_setting(fieldname: str, value: str):
	user = frappe.session.user
	if frappe.db.exists("Press Account Settings", user):
		frappe.db.set_value("Press Account Settings", user, fieldname, value)
		return

	frappe.get_doc({"doctype": "Press Account Settings", "user": user, fieldname: value}).insert(
		ignore_permissions=True
	)
