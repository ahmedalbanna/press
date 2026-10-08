import type { Dictionary } from './types';

const dialogs: Dictionary = {
	// Dialog titles
	'Remove Domain': { en: 'Remove Domain', ar: 'إزالة النطاق' },
	'Set Primary Domain': { en: 'Set Primary Domain', ar: 'تعيين النطاق الأساسي' },
	'Redirect Domain': { en: 'Redirect Domain', ar: 'إعادة توجيه النطاق' },
	'Remove Redirect': { en: 'Remove Redirect', ar: 'إزالة إعادة التوجيه' },

	// Confirmations
	'Are you sure you want to cancel the scheduled update?': {
		en: 'Are you sure you want to cancel the scheduled update?',
		ar: 'هل تريد إلغاء التحديث المجدول؟',
	},
	'Are you sure you want to delete the config <b>{key}</b>?': {
		en: 'Are you sure you want to delete the config <b>{key}</b>?',
		ar: 'هل تريد حذف الإعداد <b>{key}</b>؟',
	},
	'Are you sure you want to delete the environment variable <b>{key}</b>?': {
		en: 'Are you sure you want to delete the environment variable <b>{key}</b>?',
		ar: 'هل تريد حذف متغير البيئة <b>{key}</b>؟',
	},
	'Are you sure you want to login as administrator on the site <b>{name}</b>?': {
		en: 'Are you sure you want to login as administrator on the site <b>{name}</b>?',
		ar: 'هل تريد تسجيل الدخول كمسؤول على الموقع <b>{name}</b>؟',
	},
	'Are you sure you want to remove the app <b>{title}</b>?': {
		en: 'Are you sure you want to remove the app <b>{title}</b>?',
		ar: 'هل تريد إزالة التطبيق <b>{title}</b>؟',
	},
	'Are you sure you want to remove <b>{count}</b> app{plural}: {apps}?': {
		en: 'Are you sure you want to remove <b>{count}</b> app{plural}: {apps}?',
		ar: 'هل تريد إزالة <b>{count}</b> من التطبيقات: {apps}؟',
	},
	'Are you sure you want to remove the domain <b>{domain}</b> from the site <b>{name}</b>?': {
		en: 'Are you sure you want to remove the domain <b>{domain}</b> from the site <b>{name}</b>?',
		ar: 'هل تريد إزالة النطاق <b>{domain}</b> من الموقع <b>{name}</b>؟',
	},
	'Are you sure you want to remove the redirect from the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?': {
		en: 'Are you sure you want to remove the redirect from the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?',
		ar: 'هل تريد إزالة إعادة التوجيه من النطاق <b>{domain}</b> إلى النطاق الأساسي للموقع <b>{host}</b>؟',
	},
	'Are you sure you want to remove the tag <b>{tag}</b>?': {
		en: 'Are you sure you want to remove the tag <b>{tag}</b>?',
		ar: 'هل تريد إزالة الوسم <b>{tag}</b>؟',
	},
	'Are you sure you want to redirect the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?': {
		en: 'Are you sure you want to redirect the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?',
		ar: 'هل تريد إعادة توجيه النطاق <b>{domain}</b> إلى النطاق الأساسي للموقع <b>{host}</b>؟',
	},
	'Are you sure you want to retry fetching the certificate for the domain <b>{domain}</b>?': {
		en: 'Are you sure you want to retry fetching the certificate for the domain <b>{domain}</b>?',
		ar: 'هل تريد إعادة محاولة جلب الشهادة للنطاق <b>{domain}</b>؟',
	},
	'Are you sure you want to set the domain <b>{domain}</b> as the primary domain for the site <b>{name}</b>?': {
		en: 'Are you sure you want to set the domain <b>{domain}</b> as the primary domain for the site <b>{name}</b>?',
		ar: 'هل تريد تعيين النطاق <b>{domain}</b> كنطاق أساسي للموقع <b>{name}</b>؟',
	},
	"Are you sure you want to restore your site's database from physical backup taken on <b>{date}</b> ?": {
		en: "Are you sure you want to restore your site's database from physical backup taken on <b>{date}</b> ?",
		ar: 'هل تريد استعادة قاعدة بيانات موقعك من النسخة الاحتياطية الفيزيائية المأخوذة في <b>{date}</b>؟',
	},
	'Are you sure you want to restore your site to this offsite backup from <b>{date}</b> ?': {
		en: 'Are you sure you want to restore your site to this offsite backup from <b>{date}</b> ?',
		ar: 'هل تريد استعادة موقعك إلى هذه النسخة الاحتياطية الخارجية من <b>{date}</b>؟',
	},
	'<b>Note:</b> This action is rate limited. Please allow some time for dns changes (if any) to propagate before retrying.': {
		en: '<b>Note:</b> This action is rate limited. Please allow some time for dns changes (if any) to propagate before retrying.',
		ar: '<b>ملاحظة:</b> هذا الإجراء محدود المعدل. يُرجى الانتظار بعض الوقت حتى تنتشر تغييرات DNS (إن وجدت) قبل إعادة المحاولة.',
	},
	'The {update} failed and the {recovery} could not restore the tables.': {
		en: 'The {update} failed and the {recovery} could not restore the tables.',
		ar: 'فشلت {update} ولم تتمكن {recovery} من استعادة الجداول.',
	},
	'Re-attempt the recovery manually?': {
		en: 'Re-attempt the recovery manually?',
		ar: 'هل تريد إعادة محاولة الاستعادة يدوياً؟',
	},
	'The site database goes back to <b>{date}</b>, when the last update started. <b>Any data written to the site after that time is lost.</b> You cannot undo this.': {
		en: 'The site database goes back to <b>{date}</b>, when the last update started. <b>Any data written to the site after that time is lost.</b> You cannot undo this.',
		ar: 'تعود قاعدة بيانات الموقع إلى <b>{date}</b>، عندما بدأ التحديث الأخير. <b>أي بيانات كُتبت على الموقع بعد ذلك الوقت تُفقد.</b> لا يمكن التراجع عن هذا.',
	},

	'last update': { en: 'last update', ar: 'التحديث الأخير' },
	'automatic recovery': { en: 'automatic recovery', ar: 'الاستعادة التلقائية' },
	'Archived by {by} on {date}': { en: 'Archived by {by} on {date}', ar: 'أرشف بواسطة {by} في {date}' },
	'This site': { en: 'This site', ar: 'هذا الموقع' },
	'Investigating ': { en: 'Investigating ', ar: 'جاري التحقيق في ' },

	// Toasts: loading
	'Cancelling update...': { en: 'Cancelling update...', ar: 'جاري إلغاء التحديث...' },
	'Deleting environment variable...': { en: 'Deleting environment variable...', ar: 'جاري حذف متغير البيئة...' },
	'Deleting config...': { en: 'Deleting config...', ar: 'جاري حذف الإعداد...' },
	'Deleting snapshot...': { en: 'Deleting snapshot...', ar: 'جاري حذف اللقطة...' },
	'Fetching certificate...': { en: 'Fetching certificate...', ar: 'جاري جلب الشهادة...' },
	'Locking snapshot...': { en: 'Locking snapshot...', ar: 'جاري قفل اللقطة...' },
	'Marking all notifications as read...': { en: 'Marking all notifications as read...', ar: 'جاري تعيين كل الإشعارات كمقروءة...' },
	'Redirecting domain...': { en: 'Redirecting domain...', ar: 'جاري إعادة توجيه النطاق...' },
	'Removing App...': { en: 'Removing App...', ar: 'جاري إزالة التطبيق...' },
	'Removing Apps...': { en: 'Removing Apps...', ar: 'جاري إزالة التطبيقات...' },
	'Removing domain...': { en: 'Removing domain...', ar: 'جاري إزالة النطاق...' },
	'Removing redirect...': { en: 'Removing redirect...', ar: 'جاري إزالة إعادة التوجيه...' },
	'Removing tag...': { en: 'Removing tag...', ar: 'جاري إزالة الوسم...' },
	'Scheduling backup restore...': { en: 'Scheduling backup restore...', ar: 'جاري جدولة استعادة النسخة الاحتياطية...' },
	'Scheduling physical backup restore...': { en: 'Scheduling physical backup restore...', ar: 'جاري جدولة استعادة النسخة الاحتياطية الفيزيائية...' },
	'Setting primary domain...': { en: 'Setting primary domain...', ar: 'جاري تعيين النطاق الأساسي...' },
	'Starting table restore...': { en: 'Starting table restore...', ar: 'جاري بدء استعادة الجداول...' },
	'Unlocking snapshot...': { en: 'Unlocking snapshot...', ar: 'جاري فتح اللقطة...' },
	'Updating site...': { en: 'Updating site...', ar: 'جاري تحديث الموقع...' },
	'Fetching Latest Updates for {title}...': { en: 'Fetching Latest Updates for {title}...', ar: 'جاري جلب أحدث التحديثات لـ {title}...' },

	// Cell values
	'Awaiting Deploy': { en: 'Awaiting Deploy', ar: 'في انتظار النشر' },
	'No Expiry': { en: 'No Expiry', ar: 'بلا انتهاء' },
	'Backup on {date}': { en: 'Backup on {date}', ar: 'نسخة احتياطية في {date}' },

	// Backup dialogs
	'You will be downloading the {file} backup of the site <b>{site}</b> that was created on {date}.': {
		en: 'You will be downloading the {file} backup of the site <b>{site}</b> that was created on {date}.',
		ar: 'ستقوم بتنزيل النسخة الاحتياطية {file} للموقع <b>{site}</b> التي أُنشئت في {date}.',
	},
	'You have to be logged in as a <b>System Manager</b> <em>in your site</em> to download the backup.': {
		en: 'You have to be logged in as a <b>System Manager</b> <em>in your site</em> to download the backup.',
		ar: 'يجب أن تكون مسجلاً الدخول كـ <b>مدير النظام</b> <em>في موقعك</em> لتنزيل النسخة الاحتياطية.',
	},

	// Marketplace dialogs
	'Are you sure you want to delete this app?': {
		en: 'Are you sure you want to delete this app?',
		ar: 'هل تريد حذف هذا التطبيق؟',
	},
	'Add version support for {app}': { en: 'Add version support for {app}', ar: 'إضافة دعم الإصدار لـ {app}' },
	'Delete App {app}': { en: 'Delete App {app}', ar: 'حذف التطبيق {app}' },
	'Releases for {app} on {branch} branch': {
		en: 'Releases for {app} on {branch} branch',
		ar: 'إصدارات {app} على الفرع {branch}',
	},

	// Snapshot dialogs
	'Are you sure you want to lock this snapshot? This will prevent the snapshot from being deleted accidentally.': {
		en: 'Are you sure you want to lock this snapshot? This will prevent the snapshot from being deleted accidentally.',
		ar: 'هل تريد قفل هذه اللقطة؟ سيمنع ذلك حذف اللقطة عن طريق الخطأ.',
	},
	'Are you sure you want to unlock this snapshot ? After unlocking, the snapshot can be deleted by end-user.': {
		en: 'Are you sure you want to unlock this snapshot ? After unlocking, the snapshot can be deleted by end-user.',
		ar: 'هل تريد فتح قفل هذه اللقطة؟ بعد الفتح، يمكن للمستخدم النهائي حذف اللقطة.',
	},
	'Are you sure you want to delete this snapshot? This will delete the snapshot and all associated recovered data.': {
		en: 'Are you sure you want to delete this snapshot? This will delete the snapshot and all associated recovered data.',
		ar: 'هل تريد حذف هذه اللقطة؟ سيؤدي ذلك إلى حذف اللقطة وكل البيانات المستعادة المرتبطة بها.',
	},

	// Site action dialogs
	'Deactivate Site': { en: 'Deactivate Site', ar: 'تعطيل الموقع' },
	'Activate Site': { en: 'Activate Site', ar: 'تنشيط الموقع' },
	'Migrate Site': { en: 'Migrate Site', ar: 'ترحيل الموقع' },
	'Reset Site': { en: 'Reset Site', ar: 'إعادة تعيين الموقع' },
	'Transfer Site Ownership': { en: 'Transfer Site Ownership', ar: 'نقل ملكية الموقع' },
	'Clear Cache': { en: 'Clear Cache', ar: 'مسح الذاكرة المؤقتة' },
	'Are you sure you want to deactivate this site?': {
		en: 'Are you sure you want to deactivate this site?',
		ar: 'هل تريد تعطيل هذا الموقع؟',
	},
	'Are you sure you want to activate this site?': {
		en: 'Are you sure you want to activate this site?',
		ar: 'هل تريد تنشيط هذا الموقع؟',
	},
	'You will still be charged for it.': {
		en: 'You will still be charged for it.',
		ar: 'سيستمر تحصيل الرسوم عليك.',
	},
	'Note: Use this as last resort if site is broken and inaccessible': {
		en: 'Note: Use this as last resort if site is broken and inaccessible',
		ar: 'ملاحظة: استخدم هذا كحل أخير إذا كان الموقع معطلاً ولا يمكن الوصول إليه',
	},
	'All the data from your site will be lost. Are you sure you want to reset your database?': {
		en: 'All the data from your site will be lost. Are you sure you want to reset your database?',
		ar: 'ستفقد كل بيانات موقعك. هل تريد بالتأكيد إعادة تعيين قاعدة بياناتك؟',
	},
	'Skip patches if they fail during migration (Not recommended)': {
		en: 'Skip patches if they fail during migration (Not recommended)',
		ar: 'تخطي التصحيحات إذا فشلت أثناء الترحيل (غير مستحسن)',
	},
	'Please type the site name to confirm.': {
		en: 'Please type the site name to confirm.',
		ar: 'يُرجى كتابة اسم الموقع للتأكيد.',
	},
	'Enter email address of the team for transfer of site ownership': {
		en: 'Enter email address of the team for transfer of site ownership',
		ar: 'أدخل عنوان البريد الإلكتروني للفريق لنقل ملكية الموقع',
	},
	'Reason for transfer': { en: 'Reason for transfer', ar: 'سبب النقل' },
	'Transfer request sent to {email} successfully.': {
		en: 'Transfer request sent to {email} successfully.',
		ar: 'تم إرسال طلب النقل إلى {email} بنجاح.',
	},
	'bench migrate command will be executed on your site. Are you sure you want to run this command? We recommend that you take a database backup before continuing.': {
		en: 'bench migrate command will be executed on your site. Are you sure you want to run this command? We recommend that you take a database backup before continuing.',
		ar: 'سيتم تنفيذ أمر bench migrate على موقعك. هل تريد تشغيل هذا الأمر بالتأكيد؟ نوصي بأخذ نسخة احتياطية من قاعدة البيانات قبل المتابعة.',
	},
	'bench clear-cache and bench clear-website-cache commands will be executed on your site. Are you sure you want to run these commands?': {
		en: 'bench clear-cache and bench clear-website-cache commands will be executed on your site. Are you sure you want to run these commands?',
		ar: 'سيتم تنفيذ أمرا bench clear-cache و bench clear-website-cache على موقعك. هل تريد تشغيل هذين الأمرين بالتأكيد؟',
	},
	'General Actions': { en: 'General Actions', ar: 'إجراءات عامة' },
	'Dangerous Actions': { en: 'Dangerous Actions', ar: 'إجراءات خطيرة' },
	'Change Bench / Server / Region options moved to Migrations Tab': {
		en: 'Change Bench / Server / Region options moved to Migrations Tab',
		ar: 'تم نقل خيارات تغيير البنش / الخادم / المنطقة إلى تبويب الترحيلات',
	},
	'In-Place Migrate Site': {
		en: 'In-Place Migrate Site',
		ar: 'ترحيل الموقع في مكانه',
	},
	'Run bench migrate on the current bench to apply pending patches and schema changes.': {
		en: 'Run bench migrate on the current bench to apply pending patches and schema changes.',
		ar: 'تشغيل bench migrate على البنش الحالي لتطبيق التصحيحات وتغييرات المخطط المعلقة.',
	},
	'Move to a Different Server / Bench': {
		en: 'Move to a Different Server / Bench',
		ar: 'النقل إلى خادم / بنش مختلف',
	},
	'Move this site to another private bench or server.': {
		en: 'Move this site to another private bench or server.',
		ar: 'انقل هذا الموقع إلى بنش أو خادم خاص آخر.',
	},
	'Move to a Different Region': { en: 'Move to a Different Region', ar: 'النقل إلى منطقة مختلفة' },
	'Move this site to a bench in another region.': {
		en: 'Move this site to a bench in another region.',
		ar: 'انقل هذا الموقع إلى بنش في منطقة أخرى.',
	},
	'Move Site': { en: 'Move Site', ar: 'نقل الموقع' },
	'Site name does not match': { en: 'Site name does not match', ar: 'اسم الموقع غير مطابق' },
	'Site name does not match.': { en: 'Site name does not match.', ar: 'اسم الموقع غير مطابق.' },
	'Notification Settings': { en: 'Notification Settings', ar: 'إعدادات الإشعارات' },
	'Activate site': { en: 'Activate site', ar: 'تنشيط الموقع' },
	'Deactivate site': { en: 'Deactivate site', ar: 'تعطيل الموقع' },
	'Drop site': { en: 'Drop site', ar: 'حذف الموقع' },
	'Migrate site': { en: 'Migrate site', ar: 'ترحيل الموقع' },
	'Transfer site': { en: 'Transfer site', ar: 'نقل الموقع' },
	'Reset site': { en: 'Reset site', ar: 'إعادة تعيين الموقع' },
	'Clear cache': { en: 'Clear cache', ar: 'مسح الذاكرة المؤقتة' },
	'Schedule backup': { en: 'Schedule backup', ar: 'جدولة نسخة احتياطية' },

	// Toasts: success
	'All notifications marked as read': { en: 'All notifications marked as read', ar: 'تم تعيين كل الإشعارات كمقروءة' },
	'App Removed': { en: 'App Removed', ar: 'تم إزالة التطبيق' },
	'Apps Removed': { en: 'Apps Removed', ar: 'تم إزالة التطبيقات' },
	'App {title} added': { en: 'App {title} added', ar: 'تم إضافة التطبيق {title}' },
	'App {title} updated': { en: 'App {title} updated', ar: 'تم تحديث التطبيق {title}' },
	'Backup restore scheduled successfully.': { en: 'Backup restore scheduled successfully.', ar: 'تم جدولة استعادة النسخة الاحتياطية بنجاح.' },
	'Branch Deleted': { en: 'Branch Deleted', ar: 'تم حذف الفرع' },
	'Certificate fetch scheduled. Please wait a few minutes.': {
		en: 'Certificate fetch scheduled. Please wait a few minutes.',
		ar: 'تم جدولة جلب الشهادة. يُرجى الانتظار بضع دقائق.',
	},
	'Domain redirected': { en: 'Domain redirected', ar: 'تم إعادة توجيه النطاق' },
	'Domain removed': { en: 'Domain removed', ar: 'تم إزالة النطاق' },
	'Primary domain set': { en: 'Primary domain set', ar: 'تم تعيين النطاق الأساسي' },
	'Redirect removed': { en: 'Redirect removed', ar: 'تم إزالة إعادة التوجيه' },
	'Site update started': { en: 'Site update started', ar: 'بدأ تحديث الموقع' },
	'Table restore started': { en: 'Table restore started', ar: 'بدأت استعادة الجداول' },
	'This site is archived. It cannot be used again.': {
		en: 'This site is archived. It cannot be used again.',
		ar: 'هذا الموقع مؤرشف. لا يمكن استخدامه مرة أخرى.',
	},
	'Update cancelled': { en: 'Update cancelled', ar: 'تم إلغاء التحديث' },
	'No app changes found. The current and target benches run the same app versions, so there is nothing to update.': {
		en: 'No app changes found. The current and target benches run the same app versions, so there is nothing to update.',
		ar: 'لم يتم العثور على تغييرات في التطبيقات. البنشات الحالية والهدف تشغل نفس إصدارات التطبيقات، لذا لا يوجد شيء للتحديث.',
	},
	'Latest Updates Fetched for {title}': { en: 'Latest Updates Fetched for {title}', ar: 'تم جلب أحدث التحديثات لـ {title}' },
};

export default dialogs;
