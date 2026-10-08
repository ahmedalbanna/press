import { reactive, watch } from 'vue';
import { frappeRequest } from 'frappe-ui';
import auth from './auth';
import billing from './billing';
import common from './common';
import misc from './misc';
import nav from './nav';
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
};

interface BootGlobals {
	user?: { email?: string };
	user_language?: string;
}

const state = reactive({
	lang: (localStorage.getItem('lang') as Language) || bootLanguage() || 'en',
});

function bootLanguage(): Language | null {
	const lang = (window as unknown as BootGlobals).user_language;
	return lang === 'ar' || lang === 'en' ? lang : null;
}

export function t(key: string): string {
	return translations[key]?.[state.lang] || key;
}

export function setLanguage(lang: Language) {
	state.lang = lang;
	localStorage.setItem('lang', lang);
	saveLanguage(lang);
}

function saveLanguage(lang: Language) {
	const { user } = window as unknown as BootGlobals;
	if (!user?.email || user.email === 'Guest') {
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

const FONTS: Record<Language, string> = {
	ar: 'https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap',
	en: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap',
};

let fontLink: HTMLLinkElement | null = null;

function loadFonts(lang: Language) {
	if (!fontLink) {
		fontLink = document.createElement('link');
		fontLink.rel = 'stylesheet';
		document.head.appendChild(fontLink);
	}
	if (fontLink.href !== FONTS[lang]) {
		fontLink.href = FONTS[lang];
	}
}

export function initLanguage() {
	loadFonts(state.lang);
	watch(
		() => state.lang,
		(lang) => {
			document.documentElement.lang = lang;
			document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
			loadFonts(lang);
		},
		{ immediate: true },
	);
}

export default {
	t,
	setLanguage,
	getLanguage,
	isRTL,
	initLanguage,
};
