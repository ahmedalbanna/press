import { reactive, watch } from 'vue';

export type Language = 'en' | 'ar';

const translations: Record<string, Record<Language, string>> = {
	'Dashboard': { en: 'Dashboard', ar: 'لوحة التحكم' },
	'Sites': { en: 'Sites', ar: 'المواقع' },
	'Billing': { en: 'Billing', ar: 'الفوترة' },
	'Servers': { en: 'Servers', ar: 'الخوادم' },
	'Apps': { en: 'Apps', ar: 'التطبيقات' },
	'Settings': { en: 'Settings', ar: 'الإعدادات' },
	'Logout': { en: 'Logout', ar: 'تسجيل الخروج' },
	'Change Team': { en: 'Change Team', ar: 'تغيير الفريق' },
	'Theme': { en: 'Theme', ar: 'المظهر' },
	'Light Mode': { en: 'Light Mode', ar: 'الوضع الفاتح' },
	'Dark Mode': { en: 'Dark Mode', ar: 'الوضع الداكن' },
	'Become a Partner': { en: 'Become a Partner', ar: 'كن شريكاً' },
	'Docs': { en: 'Docs', ar: 'التوثيق' },
	'Get Support': { en: 'Get Support', ar: 'الحصول على الدعم' },
	'Share Feedback': { en: 'Share Feedback', ar: 'مشاركة الملاحظات' },
	'Find a Partner': { en: 'Find a Partner', ar: 'البحث عن شريك' },
	'Release Notes': { en: 'Release Notes', ar: 'ملاحظات الإصدار' },
	'Loading...': { en: 'Loading...', ar: 'جاري التحميل...' },
	'Save': { en: 'Save', ar: 'حفظ' },
	'Cancel': { en: 'Cancel', ar: 'إلغاء' },
	'Delete': { en: 'Delete', ar: 'حذف' },
	'Edit': { en: 'Edit', ar: 'تعديل' },
	'Create': { en: 'Create', ar: 'إنشاء' },
	'Search': { en: 'Search', ar: 'بحث' },
	'Close': { en: 'Close', ar: 'إغلاق' },
	'Back': { en: 'Back', ar: 'رجوع' },
	'Next': { en: 'Next', ar: 'التالي' },
	'Submit': { en: 'Submit', ar: 'إرسال' },
	'Confirm': { en: 'Confirm', ar: 'تأكيد' },
	'Log in to your AlbannaTech account': { en: 'Log in to your AlbannaTech account', ar: 'تسجيل الدخول إلى حساب AlbannaTech الخاص بك' },
	'Signup to your AlbannaTech account': { en: 'Signup to your AlbannaTech account', ar: 'إنشاء حساب AlbannaTech جديد' },
	'Email': { en: 'Email', ar: 'البريد الإلكتروني' },
	'Password': { en: 'Password', ar: 'كلمة المرور' },
	'Forgot Password?': { en: 'Forgot Password?', ar: 'نسيت كلمة المرور؟' },
	'Login': { en: 'Login', ar: 'تسجيل الدخول' },
	'Signup': { en: 'Signup', ar: 'إنشاء حساب' },
	'Create Account': { en: 'Create Account', ar: 'إنشاء حساب' },
	'Welcome to AlbannaTech': { en: 'Welcome to AlbannaTech', ar: 'مرحباً بك في AlbannaTech' },
	'AlbannaTech makes it easy to manage sites and apps like ERPNext in an': { en: 'AlbannaTech makes it easy to manage sites and apps like ERPNext in an', ar: 'AlbannaTech تجعل من السهل إدارة المواقع والتطبيقات مثل ERPNext في' },
	'Please contact AlbannaTech support by clicking on the button below.': { en: 'Please contact AlbannaTech support by clicking on the button below.', ar: 'يرجى التواصل مع دعم AlbannaTech بالنقر على الزر أدناه.' },
};

const state = reactive({
	lang: (localStorage.getItem('lang') as Language) || 'en',
});

export function t(key: string): string {
	return translations[key]?.[state.lang] || key;
}

export function setLanguage(lang: Language) {
	state.lang = lang;
	localStorage.setItem('lang', lang);
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
	setLanguage,
	getLanguage,
	isRTL,
	initLanguage,
};
