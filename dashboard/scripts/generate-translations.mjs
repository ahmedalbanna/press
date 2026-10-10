#!/usr/bin/env node
/*
 * Emits press/locale/ar.po from the dashboard dictionaries.
 *
 * Frappe resolves _() inside an email template through the app's translation
 * catalog, while the SPA reads the TypeScript dictionaries. The catalog used to
 * be a hand-maintained CSV, so the same English string could carry different
 * Arabic depending on which surface rendered it -- eight did.
 *
 * Two further surfaces had no Arabic at all: the Desk UI, whose labels live in
 * doctype JSON that no extractor reads, and the framework chrome around it. The
 * catalog is now a single gettext PO file merging all three, and the CSV is
 * gone:
 *
 *   1. the dictionaries (source of truth for the SPA and email templates),
 *   2. press/locale/main.pot, which `bench generate-pot-file --app press`
 *      extracts from doctypes, Python and JS -- where the Desk labels come
 *      from, and the only way to know which strings exist,
 *   3. frappe/locale/ar.po as translation memory, so the framework's own Arabic
 *      for a shared string ("Save", "Submit", "Amend") is not written twice.
 *
 * A msgid present in several sources resolves dictionaries > prior PO >
 * framework memory, so translator edits survive a re-extraction.
 *
 * The file is committed as well as generated: `bench build` compiles it to
 * sites/assets/locale/ar/LC_MESSAGES/press.mo, and
 * press/tests/test_translation_catalog.py fails if the two disagree.
 *
 * main.pot is *not* committed -- .gitignore excludes *.pot, as in frappe -- and
 * ar.po alone is enough to share and to keep every existing translation, because
 * entries it already holds take priority over anything re-extracted. Regenerate
 * the POT first when adding a new doctype or field label; until then this warns
 * and the new string simply has no Arabic yet.
 *
 * `bench build` compiles this file to MO but does not flush the cached
 * translation catalog, so after adding or editing a string also run
 * `bench --site <site> clear-cache` (or restart the web process). Without it the
 * runtime keeps serving the previous catalog and a fresh translation looks
 * exactly like a missing one.
 *
 * Run directly (`node dashboard/scripts/generate-translations.mjs`) or via
 * `yarn build`, which wires it in ahead of the CSS builds.
 *
 * Requires Node >= 22.6 for TypeScript type stripping.
 */
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const langDir = join(here, '..', 'src', 'utils', 'language')
// The press app package: apps/press/press. `here` is apps/press/dashboard/scripts,
// so it is two levels up and then into the app, matching how the tests resolve it.
const appRoot = join(here, '..', '..', 'press')
const potFile = join(appRoot, 'locale', 'main.pot')
const outFile = join(appRoot, 'locale', 'ar.po')
// The control bench's frappe app, used purely as translation memory.
const frameworkFile = join(
	appRoot,
	'..',
	'..',
	'frappe',
	'frappe',
	'locale',
	'ar.po',
)

// Order is the merge order in language/index.ts, so a duplicate keeps the same
// winner here as it does at runtime.
const MODULES = [
	'nav',
	'common',
	'auth',
	'onboarding',
	'sites',
	'servers',
	'billing',
	'team',
	'misc',
	'objects',
	'dialogs',
	'emails',
]

/* ---------------------------------------------------------------- PO reading */

/** In PO, a line opening with a bare quote continues the previous string. */
function joinContinuations(lines) {
	const joined = []
	for (const line of lines) {
		if (line.startsWith('"') && joined.length) joined[joined.length - 1] += line
		else joined.push(line)
	}
	return joined
}

/** All quoted tokens on one logical line, concatenated and unescaped. */
function quotedValue(line) {
	let out = ''
	const re = /"((?:[^"\\]|\\.)*)"/g
	let match = re.exec(line)
	while (match) {
		out += unescape(match[1])
		match = re.exec(line)
	}
	return out
}

function unescape(token) {
	let out = ''
	for (let i = 0; i < token.length; i++) {
		if (token[i] !== '\\') {
			out += token[i]
			continue
		}
		const next = token[++i]
		switch (next) {
			case 'n':
				out += '\n'
				break
			case 't':
				out += '\t'
				break
			case 'r':
				out += '\r'
				break
			case '"':
			case '\\':
				out += next
				break
			default:
				// Unknown escape: keep the backslash rather than eat a character.
				out += `\\${next ?? ''}`
		}
	}
	return out
}

/**
 * Parse a PO file into { header, entries }. Comments are carried through
 * verbatim, so `#: file:line` references and translator notes survive without
 * this script needing to understand them.
 */
function parsePo(text) {
	const lines = joinContinuations(text.split('\n'))
	const entries = []
	let header = null
	let pending = []
	let entry = null

	const close = () => {
		if (entry && entry !== header) entries.push(entry)
		entry = null
	}

	for (const line of lines) {
		if (line.trim() === '') {
			close()
			pending = []
			continue
		}
		if (line.startsWith('#')) {
			close()
			pending.push(line)
			continue
		}
		if (/^msgctxt\b/.test(line)) {
			close()
			entry = {
				comments: pending,
				msgctxt: quotedValue(line),
				msgid: '',
				msgstr: '',
			}
			pending = []
			continue
		}
		if (/^msgid\b/.test(line)) {
			close()
			entry = {
				comments: pending,
				msgctxt: '',
				msgid: quotedValue(line),
				msgstr: '',
			}
			pending = []
			continue
		}
		if (/^msgstr\b/.test(line)) {
			// A msgstr before any msgid is the header entry.
			if (!entry) {
				header = { comments: pending, msgid: '', msgstr: quotedValue(line) }
				entry = header
			} else {
				entry.msgstr = quotedValue(line)
			}
			pending = []
			continue
		}
		// msgid_plural and anything else this app does not extract.
	}
	close()
	return { header, entries }
}

/* ---------------------------------------------------------------- PO writing */

function escapePo(value) {
	return String(value)
		.replace(/\\/g, '\\\\')
		.replace(/"/g, '\\"')
		.replace(/\t/g, '\\t')
		.replace(/\r/g, '\\r')
		.replace(/\n/g, '\\n')
}

const compareKeys = (a, b) =>
	a.msgid.localeCompare(b.msgid, 'en', { sensitivity: 'base' }) ||
	(a.msgctxt || '').localeCompare(b.msgctxt || '', 'en', {
		sensitivity: 'base',
	})

function writePo(header, entries) {
	const out = []
	for (const line of header.comments) out.push(line)
	out.push('msgid ""')
	out.push(`msgstr "${escapePo(header.msgstr)}"`)
	out.push('')
	for (const entry of entries) {
		for (const line of entry.comments) out.push(line)
		if (entry.msgctxt) out.push(`msgctxt "${escapePo(entry.msgctxt)}"`)
		out.push(`msgid "${escapePo(entry.msgid)}"`)
		out.push(`msgstr "${escapePo(entry.msgstr)}"`)
		out.push('')
	}
	return out.join('\n') + '\n'
}

/* ------------------------------------------------------------------- sources */

const merged = {}
const sources = {}
for (const name of MODULES) {
	const mod = await import(join(langDir, `${name}.ts`))
	for (const [key, value] of Object.entries(mod.default)) {
		if (merged[key] !== undefined) {
			console.warn(
				`duplicate key ${JSON.stringify(key)} in ${name}.ts, ` +
					`overriding ${sources[key]}`,
			)
		}
		merged[key] = value
		sources[key] = `${name}.ts`
	}
}

const problems = []
for (const [key, value] of Object.entries(merged)) {
	if (!value || typeof value.ar !== 'string' || !value.ar.trim()) {
		problems.push(`${key}: missing or empty "ar"`)
		continue
	}
	if (value.en !== undefined && value.en !== key) {
		problems.push(
			`${key}: en is ${JSON.stringify(value.en)}, expected the key itself`,
		)
	}
	if (/[一-鿿Ѐ-ӿ가-힯]/.test(value.ar)) {
		problems.push(`${key}: Arabic translation contains a non-Arabic script`)
	}
}
if (problems.length) {
	console.error('translation problems:\n  ' + problems.join('\n  '))
	process.exit(1)
}

/* --------------------------------------------------------------- merge order */

const keyOf = (msgid, msgctxt = '') => `${msgctxt}\u0004${msgid}`

// The POT is the inventory of Desk-side strings. Without it we can only carry
// what we already know, which is how ar.po regenerates after a re-extraction.
const pot = existsSync(potFile)
	? parsePo(readFileSync(potFile, 'utf8'))
	: { entries: [] }
if (!pot.entries.length) {
	console.warn(
		`no msgids found in ${potFile}; ` +
			'run `bench --site <site> generate-pot-file --app press`',
	)
}

const previous = existsSync(outFile)
	? parsePo(readFileSync(outFile, 'utf8'))
	: { header: null, entries: [] }
const prior = new Map()
for (const entry of previous.entries) {
	if (entry.msgid) prior.set(keyOf(entry.msgid, entry.msgctxt), entry)
}

const memory = new Map()
// Frappe's runtime falls back from a context-keyed translation to a plain one
// (get_translations_from_mo), and the framework catalog is far more likely to
// carry a context than our POT is, so the same fallback is applied here.
const memoryById = new Map()
if (existsSync(frameworkFile)) {
	const { entries } = parsePo(readFileSync(frameworkFile, 'utf8'))
	let loaded = 0
	for (const entry of entries) {
		if (!entry.msgid || !entry.msgstr) continue
		const key = keyOf(entry.msgid, entry.msgctxt)
		if (!memory.has(key)) {
			memory.set(key, entry.msgstr)
			loaded++
		}
		if (!memoryById.has(entry.msgid)) memoryById.set(entry.msgid, entry.msgstr)
	}
	console.log(`loaded ${loaded} framework translations as memory`)
}

const byKey = new Map()
const claim = (msgid, msgctxt = '') => {
	const key = keyOf(msgid, msgctxt)
	if (!byKey.has(key))
		byKey.set(key, { msgid, msgctxt, comments: [], msgstr: '' })
	return byKey.get(key)
}

for (const entry of pot.entries) {
	// `msgid ""` is the POT's header, not a string to translate.
	if (!entry.msgid) continue
	claim(entry.msgid, entry.msgctxt).comments = [...entry.comments]
}
for (const key of Object.keys(merged)) {
	// A msgid only the SPA uses has no POT reference, so name the source here
	// rather than leaving a translator to guess.
	claim(key, '').comments = [
		`#. From dashboard/src/utils/language/${sources[key]}`,
	]
}
// Anything the PO still holds but the POT no longer extracts is kept verbatim,
// so re-extraction cannot silently drop a finished translation.
for (const [key, entry] of prior) {
	if (!entry.msgid || byKey.has(key)) continue
	byKey.set(key, {
		msgid: entry.msgid,
		msgctxt: entry.msgctxt,
		comments: [
			...(entry.comments ?? []),
			'#. No longer extracted; translation retained',
		],
		msgstr: entry.msgstr,
	})
}

// Resolve: dictionaries > prior PO > framework memory.
let fromDictionaries = 0
let fromPrior = 0
let fromMemory = 0
let untranslated = 0
for (const entry of byKey.values()) {
	const dict = merged[entry.msgid]
	if (entry.msgctxt === '' && dict?.ar) {
		entry.msgstr = dict.ar
		fromDictionaries++
		continue
	}
	if (prior.get(keyOf(entry.msgid, entry.msgctxt))?.msgstr) {
		entry.msgstr = prior.get(keyOf(entry.msgid, entry.msgctxt)).msgstr
		fromPrior++
		continue
	}
	const remembered =
		memory.get(keyOf(entry.msgid, entry.msgctxt)) ?? memoryById.get(entry.msgid)
	if (remembered) {
		entry.msgstr = remembered
		fromMemory++
		continue
	}
	untranslated++
}

// escapePo() turns real newlines into \n, so these need no pre-escaping.
const header = {
	comments: [
		'# Arabic translation for the AlbannaTech Press app.',
		'# Copyright (C) 2026 AlbannaTech',
		'# This file is distributed under the same license as the AlbannaTech project.',
	],
	msgstr:
		[
			'Project-Id-Version: AlbannaTech',
			'Report-Msgid-Bugs-To: support@albannatech.com',
			'POT-Creation-Date: 2026-10-10 20:00+0000',
			'PO-Revision-Date: 2026-10-10 20:00+0000',
			'Last-Translator: support@albannatech.com',
			'Language-Team: Arabic',
			'Language: ar',
			'MIME-Version: 1.0',
			'Content-Type: text/plain; charset=UTF-8',
			'Content-Transfer-Encoding: 8bit',
			'Plural-Forms: nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);',
		].join('\n') + '\n',
}

writeFileSync(
	outFile,
	writePo(header, [...byKey.values()].sort(compareKeys)),
	'utf8',
)

console.log(
	`wrote ${byKey.size} msgids to ${outFile.replace(process.cwd() + '/', '')}\n` +
		`  ${fromDictionaries} from the dictionaries, ${fromPrior} from the previous PO,\n` +
		`  ${fromMemory} from framework memory, ${untranslated} awaiting Arabic`,
)
