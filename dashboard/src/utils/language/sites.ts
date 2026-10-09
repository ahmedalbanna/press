import type { Dictionary } from './types';

const sites: Dictionary = {
	// Sites
	'Site': { en: 'Site', ar: 'موقع' },
	'Site Name': { en: 'Site Name', ar: 'اسم الموقع' },
	'Site Domain': { en: 'Site Domain', ar: 'نطاق الموقع' },
	'Site URL': { en: 'Site URL', ar: 'رابط الموقع' },
	'Site Status': { en: 'Site Status', ar: 'حالة الموقع' },
	'Site Plan': { en: 'Site Plan', ar: 'خطة الموقع' },
	'Site Analytics': { en: 'Site Analytics', ar: 'تحليلات الموقع' },
	'Site Logs': { en: 'Site Logs', ar: 'سجلات الموقع' },
	'Site Jobs': { en: 'Site Jobs', ar: 'مهام الموقع' },
	'Site Update': { en: 'Site Update', ar: 'تحديث الموقع' },
	'Site Detail': { en: 'Site Detail', ar: 'تفاصيل الموقع' },
	'Site List': { en: 'Site List', ar: 'قائمة المواقع' },
	'Site Performance': { en: 'Site Performance', ar: 'أداء الموقع' },
	'Site Database': { en: 'Site Database', ar: 'قاعدة بيانات الموقع' },
	'Site Backup': { en: 'Site Backup', ar: 'نسخ احتياطي للموقع' },
	'Site Migration': { en: 'Site Migration', ar: 'ترحيل الموقع' },
	'Site Version': { en: 'Site Version', ar: 'إصدار الموقع' },
	'Site Settings': { en: 'Site Settings', ar: 'إعدادات الموقع' },
	'Site Users': { en: 'Site Users', ar: 'مستخدمي الموقع' },
	'Site Files': { en: 'Site Files', ar: 'ملفات الموقع' },
	'Site Email': { en: 'Site Email', ar: 'بريد الموقع' },
	'Site Notification': { en: 'Site Notification', ar: 'إشعارات الموقع' },
	'Site Activity': { en: 'Site Activity', ar: 'نشاط الموقع' },
	'Site Health': { en: 'Site Health', ar: 'صحة الموقع' },
	'Site Uptime': { en: 'Site Uptime', ar: 'وقت تشغيل الموقع' },
	'Site Downtime': { en: 'Site Downtime', ar: 'وقت توقف الموقع' },
	'Site SSL': { en: 'Site SSL', ar: 'شهادة SSL للموقع' },
	'Site Subdomain': { en: 'Site Subdomain', ar: 'النطاق الفرعي للموقع' },

	// Sites list page (pages/sites/list/Page.vue). Status values double as
	// filter values, so the English enum stays the option value and only the
	// displayed label is translated.
	'Installing': { en: 'Installing', ar: 'قيد التثبيت' },
	'Export as CSV': { en: 'Export as CSV', ar: 'تصدير كملف CSV' },
	'Search sites': { en: 'Search sites', ar: 'البحث في المواقع' },
	'Site Actions': { en: 'Site Actions', ar: 'إجراءات الموقع' },
	'Shared': { en: 'Shared', ar: 'مشترك' },
	'Go to site dashboard': { en: 'Go to site dashboard', ar: 'الانتقال إلى لوحة تحكم الموقع' },
	'No sites': { en: 'No sites', ar: 'لا توجد مواقع' },
	'site': { en: 'site', ar: 'موقع' },
	'sites': { en: 'sites', ar: 'مواقع' },
	'Your team has no live sites. This page shows your archived sites.': {
		en: 'Your team has no live sites. This page shows your archived sites.',
		ar: 'لا يملك فريقك أي مواقع نشطة. تعرض هذه الصفحة مواقعك المؤرشفة.',
	},
};

export default sites;
