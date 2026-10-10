import { frappeRequest } from "frappe-ui";
import { onMounted, ref } from "vue";

export type Theme = "light" | "dark" | "system";

interface BootGlobals {
	user_theme?: string;
	available_themes?: { theme_name: string; label: string; tokens: Record<string, string> }[];
}

// Reactive mirror of the data-theme attribute, so menus and labels can show
// the active theme (a checkmark, a toggle state) without reading the DOM.
// The attribute stays the source of truth for CSS; this ref is kept in sync
// by setTheme, the only writer.
export const themeName = ref<Theme>(
	(typeof localStorage !== "undefined" && (localStorage.getItem("theme") as Theme)) ||
		"light",
);

const LOCAL_STORAGE_KEY = "theme";

// Themes are stored as Press Theme records and sent in the boot payload, so a
// theme's colours are edited in Desk rather than in the stylesheet. The CSS in
// global.css stays as the fallback for a theme with no rows yet.
function themesFromBoot(): Record<string, Record<string, string>> {
	const themes = (window as unknown as BootGlobals).available_themes ?? [];
	return Object.fromEntries(themes.map((theme) => [theme.theme_name, theme.tokens]));
}

function themeFromBoot(): Theme | null {
	const name = (window as unknown as BootGlobals).user_theme;
	return name === "light" || name === "dark" || name === "system" ? name : null;
}

// Inline styles win over the stylesheet, so a theme's tokens must be removed
// before the next theme's are applied or they would stack up and the last
// writer would win for the rest of the session.
const appliedTokenNames = new Set<string>();

function applyTokens(theme: string, tokens: Record<string, string> | undefined) {
	for (const name of appliedTokenNames) {
		document.documentElement.style.removeProperty(`--${name}`);
	}
	appliedTokenNames.clear();

	if (!tokens) return;
	for (const [name, value] of Object.entries(tokens)) {
		document.documentElement.style.setProperty(`--${name}`, value);
		appliedTokenNames.add(name);
	}
}

// The theme the server says the account uses, remembered so it can be
// re-applied on the next load before first paint.
let serverTheme: Theme | null = null;

// "system" is derived from the OS, so there is nothing to store for it.
function saveTheme(name: Theme) {
	if (name === "system") return;
	void frappeRequest({
		url: "/api/method/press.api.account.set_theme",
		method: "POST",
		// frappe-ui serialises `params` into the request body. Passing `args`
		// silently sends no payload and the call 500s.
		params: { theme: name },
	}).catch(() => {
		// The preference stays in localStorage if the save fails.
	});
}

export function getTheme(): Theme {
	return themeName.value;
}

export const setTheme = (name: Theme) => {
	document.documentElement.classList.add("no-transition");

	document.documentElement.setAttribute("data-theme", name);
	applyTokens(name, themesFromBoot()[name]);
	localStorage.setItem(LOCAL_STORAGE_KEY, name);
	themeName.value = name;

	serverTheme = themeFromBoot();
	saveTheme(name);

	requestAnimationFrame(() => {
		requestAnimationFrame(() => {
			document.documentElement.classList.remove("no-transition");
		});
	});
};

export const initTheme = () => {
	onMounted(() => {
		const storedTheme = localStorage.getItem(LOCAL_STORAGE_KEY) as Theme | null;

		// The server preference outranks this device's stored value, so the
		// account's choice follows the user to a new browser. A device that
		// never saw the preference keeps its stored theme.
		const theme = themeFromBoot() ?? storedTheme ?? "light";
		serverTheme = themeFromBoot();
		setTheme(theme);
	});
};

// The theme the server says the account uses, for the theme picker to show a
// checkmark.
export const getServerTheme = (): Theme | null => serverTheme;

// Themes offered by the account, for the picker to build its rows from.
export interface AvailableTheme {
	theme_name: string;
	label: string;
}

export const getAvailableThemes = (): AvailableTheme[] =>
	(window as unknown as BootGlobals).available_themes ?? [];
