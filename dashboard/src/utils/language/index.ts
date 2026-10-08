import { reactive, watch } from 'vue';
import { frappeRequest } from 'frappe-ui';
import auth from './auth';
import billing from './billing';
import common from './common';
import dialogs from './dialogs';
import misc from './misc';
import nav from './nav';
import objects from './objects';
import onboarding from './onboarding';
import servers from './servers';
import sites from './sites';
import team from './team';
import type { Dictionary, Language } from './types';

export type { Language };

const translations: Dictionary = {
	...nav,
	...common,
	...auth,
	...onboarding,
	...sites,
	...servers,
	...billing,
	...team,
	...misc,
	...objects,
	...dialogs,
};

interface BootGlobals {
	user_email?: string;
	user_language?: string;
}

// Precedence: the server-side per-user preference wins, because it is the one
// that follows the user across devices and is what an admin can change for
// them. localStorage is only a fallback for when there is no server value yet
// (first visit, or a save that failed), so a language picked on this device
// still survives a reload.
const state = reactive({
	lang: bootLanguage() || (localStorage.getItem('lang') as Language) || 'en',
});

function bootLanguage(): Language | null {
	const lang = (window as unknown as BootGlobals).user_language;
	return lang === 'ar' || lang === 'en' ? lang : null;
}

export function t(key: string): string {
	return translations[key]?.[state.lang] || key;
}

// Same as t(), but fills {name} placeholders so interpolated sentences stay
// translatable as a whole instead of being glued from fragments
export function tr(key: string, values?: Record<string, string | number>): string {
	let message = t(key);
	if (values) {
		for (const [name, value] of Object.entries(values)) {
			message = message.replaceAll(`{${name}}`, String(value));
		}
	}
	return message;
}

export function setLanguage(lang: Language) {
	state.lang = lang;
	localStorage.setItem('lang', lang);
	saveLanguage(lang);
}

function saveLanguage(lang: Language) {
	const email = (window as unknown as BootGlobals).user_email;
	if (!email || email === 'Guest') {
		return;
	}
	void frappeRequest({
		url: '/api/method/press.api.account.set_language',
		method: 'POST',
		args: { language: lang },
	}).catch(() => {
		// preference stays in localStorage if the save fails
	});
}

export function getLanguage(): Language {
	return state.lang;
}

export function isRTL(): boolean {
	return state.lang === 'ar';
}

export function initLanguage() {
	watch(
		() => state.lang,
		(lang) => {
			document.documentElement.lang = lang;
			document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
		},
		{ immediate: true },
	);
}

export default {
	t,
	tr,
	setLanguage,
	getLanguage,
	isRTL,
	initLanguage,
};
