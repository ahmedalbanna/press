#!/usr/bin/env node
/*
 * Emits press/translations/ar.csv from the dashboard dictionaries.
 *
 * Frappe resolves _() inside an email template through the app's translation
 * catalog, so before this existed the same English string had two homes: the
 * TS dictionaries for the SPA, and a hand-maintained CSV for email. Eight
 * strings were in both with different Arabic, so they rendered differently
 * depending on which surface produced them.
 *
 * The dictionaries are the larger surface and the one the interface is built
 * from, so they are the source. This script exists so the catalog cannot fall
 * behind them.
 *
 * Run directly (`node dashboard/scripts/generate-translations.mjs`) or via
 * `yarn build`, which wires it in ahead of the CSS builds. The output is
 * committed as well as generated: Frappe needs it present on a fresh checkout,
 * and press/tests/test_translation_catalog.py fails if the two disagree.
 *
 * Requires Node >= 22.6 for TypeScript type stripping.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const langDir = join(here, "..", "src", "utils", "language");
const outFile = join(here, "..", "..", "press", "translations", "ar.csv");

// Order is the merge order in language/index.ts, so a duplicate keeps the same
// winner here as it does at runtime.
const MODULES = [
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
];

/** Quote a field only when it contains a comma, quote or newline. */
function csvField(value) {
	const text = String(value);
	if (/[",\n\r]/.test(text)) {
		return `"${text.replace(/"/g, '""')}"`;
	}
	return text;
}

const merged = {};
const sources = {};
for (const name of MODULES) {
	const mod = await import(join(langDir, `${name}.ts`));
	for (const [key, value] of Object.entries(mod.default)) {
		if (merged[key] !== undefined) {
			// Matches language/index.ts: later modules win. Duplicates across
			// modules are how the same string drifted in the first place.
			console.warn(
				`duplicate key ${JSON.stringify(key)} in ${name}.ts, ` +
					`overriding ${sources[key]}`,
			);
		}
		merged[key] = value;
		sources[key] = `${name}.ts`;
	}
}

const problems = [];
for (const [key, value] of Object.entries(merged)) {
	if (!value || typeof value.ar !== "string" || !value.ar.trim()) {
		problems.push(`${key}: missing or empty "ar"`);
		continue;
	}
	if (value.en !== undefined && value.en !== key) {
		// t() falls back to the key, so "en" drifting from it means the SPA
		// shows one string and Frappe looks up another.
		problems.push(
			`${key}: en is ${JSON.stringify(value.en)}, expected the key itself`,
		);
	}
	if (/[一-鿿Ѐ-ӿ가-힯]/.test(value.ar)) {
		problems.push(`${key}: Arabic translation contains a non-Arabic script`);
	}
}

if (problems.length) {
	console.error("translation problems:\n  " + problems.join("\n  "));
	process.exit(1);
}

const rows = Object.keys(merged)
	.sort()
	.map((key) => `${csvField(key)},${csvField(merged[key].ar)}`);

writeFileSync(outFile, `${rows.join("\n")}\n`, "utf8");
console.log(
	`wrote ${rows.length} Arabic translations to ${outFile.replace(
		process.cwd() + "/",
		"",
	)}`,
);