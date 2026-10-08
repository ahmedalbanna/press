import type { Dictionary } from './types';

const billing: Dictionary = {
	// Billing
	'Prepaid Credits': { en: 'Prepaid Credits', ar: 'رصيد مسبق الدفع' },
	'Credit Balance': { en: 'Credit Balance', ar: 'الرصيد المتبقي' },
	'Add Credit': { en: 'Add Credit', ar: 'إضافة رصيد' },
	'Add Credits': { en: 'Add Credits', ar: 'إضافة رصيد' },
	'Billing Overview': { en: 'Billing Overview', ar: 'نظرة عامة على الفوترة' },
	'Billing History': { en: 'Billing History', ar: 'سجل الفوترة' },
	'Billing Details': { en: 'Billing Details', ar: 'تفاصيل الفوترة' },
	'Billing Settings': { en: 'Billing Settings', ar: 'إعدادات الفوترة' },
	'Billing Address': { en: 'Billing Address', ar: 'عنوان الفوترة' },
	'Billing Contact': { en: 'Billing Contact', ar: 'جهات اتصال الفوترة' },
	'Billing Email': { en: 'Billing Email', ar: 'بريد الفوترة' },
	'Billing Phone': { en: 'Billing Phone', ar: 'هاتف الفوترة' },
	'Billing Country': { en: 'Billing Country', ar: 'دولة الفوترة' },
	'Billing City': { en: 'Billing City', ar: 'مدينة الفوترة' },
	'Billing State': { en: 'Billing State', ar: 'ولاية الفوترة' },
	'Billing Zip': { en: 'Billing Zip', ar: 'رمز الفوترة البريدي' },
	'Billing Postal Code': { en: 'Billing Postal Code', ar: 'الرمز البريدي للفوترة' },
	'Invoice': { en: 'Invoice', ar: 'فاتورة' },
	'Invoices': { en: 'Invoices', ar: 'فواتير' },
	'Invoice Number': { en: 'Invoice Number', ar: 'رقم الفاتورة' },
	'Invoice Date': { en: 'Invoice Date', ar: 'تاريخ الفاتورة' },
	'Invoice Amount': { en: 'Invoice Amount', ar: 'مبلغ الفاتورة' },
	'Invoice Status': { en: 'Invoice Status', ar: 'حالة الفاتورة' },
	'Invoice Due Date': { en: 'Invoice Due Date', ar: 'تاريخ استحقاق الفاتورة' },
	'Invoice Paid Date': { en: 'Invoice Paid Date', ar: 'تاريخ دفع الفاتورة' },
	'Invoice Overdue': { en: 'Invoice Overdue', ar: 'فاتورة متأخرة' },
	'Invoice Paid': { en: 'Invoice Paid', ar: 'فاتورة مدفوعة' },
	'Invoice Unpaid': { en: 'Invoice Unpaid', ar: 'فاتورة غير مدفوعة' },
	'Invoice Partial': { en: 'Invoice Partial', ar: 'فاتورة جزئية' },
	'Invoice Refunded': { en: 'Invoice Refunded', ar: 'فاتورة مستردة' },
	'Invoice Cancelled': { en: 'Invoice Cancelled', ar: 'فاتورة ملغاة' },
	'Payment': { en: 'Payment', ar: 'دفع' },
	'Payments': { en: 'Payments', ar: 'مدفوعات' },
	'Payment Method': { en: 'Payment Method', ar: 'طريقة الدفع' },
	'Payment Methods': { en: 'Payment Methods', ar: 'طرق الدفع' },
	'Payment Gateway': { en: 'Payment Gateway', ar: 'بوابة الدفع' },
	'Payment Gateways': { en: 'Payment Gateways', ar: 'بوابات الدفع' },
	'Payment Status': { en: 'Payment Status', ar: 'حالة الدفع' },
	'Payment Date': { en: 'Payment Date', ar: 'تاريخ الدفع' },
	'Payment Amount': { en: 'Payment Amount', ar: 'مبلغ الدفع' },
	'Payment Currency': { en: 'Payment Currency', ar: 'عملة الدفع' },
	'Payment Reference': { en: 'Payment Reference', ar: 'مرجع الدفع' },
	'Payment Transaction': { en: 'Payment Transaction', ar: 'معاملة الدفع' },
	'Payment Receipt': { en: 'Payment Receipt', ar: 'إيصال الدفع' },
	'Payment Confirmation': { en: 'Payment Confirmation', ar: 'تأكيد الدفع' },
	'Payment Failure': { en: 'Payment Failure', ar: 'فشل الدفع' },
	'Payment Success': { en: 'Payment Success', ar: 'نجاح الدفع' },
	'Payment Pending': { en: 'Payment Pending', ar: 'دفع قيد الانتظار' },
	'Payment Processing': { en: 'Payment Processing', ar: 'جاري معالجة الدفع' },
	'Payment Completed': { en: 'Payment Completed', ar: 'دفع مكتمل' },
	'Payment Failed': { en: 'Payment Failed', ar: 'فشل الدفع' },
	'Payment Refunded': { en: 'Payment Refunded', ar: 'دفع مسترد' },
	'Payment Cancelled': { en: 'Payment Cancelled', ar: 'دفع ملغي' },
	'Payment Disputed': { en: 'Payment Disputed', ar: 'دفع متنازع عليه' },
	'Payment Chargeback': { en: 'Payment Chargeback', ar: 'استرداد دفع' },
	// Billing page tabs
	'Subscriptions': { en: 'Subscriptions', ar: 'الاشتراكات' },
	'Forecast': { en: 'Forecast', ar: 'التوقعات' },
	'Balances': { en: 'Balances', ar: 'الأرصدة' },
	'Marketplace Payouts': { en: 'Marketplace Payouts', ar: 'مدفوعات السوق' },
	'Limits': { en: 'Limits', ar: 'الحدود' },
	'UPI Autopay': { en: 'UPI Autopay', ar: 'الدفع التلقائي عبر UPI' },
	"You aren't permitted to view the billing page": {
		en: "You aren't permitted to view the billing page",
		ar: 'غير مسموح لك بعرض صفحة الفوترة',
	},
	// BillingInvoices
	'Nothing to show': { en: 'Nothing to show', ar: 'لا شيء لعرضه' },
	'Draft': { en: 'Draft', ar: 'مسودة' },
	'Invoice Created': { en: 'Invoice Created', ar: 'تم إنشاء الفاتورة' },
	'Unpaid': { en: 'Unpaid', ar: 'غير مدفوعة' },
	'Refunded': { en: 'Refunded', ar: 'مستردة' },
	'Uncollectible': { en: 'Uncollectible', ar: 'غير قابلة للتحصيل' },
	'Collected': { en: 'Collected', ar: 'تم التحصيل' },
	'Empty': { en: 'Empty', ar: 'فارغة' },
	'Partnership Fees': { en: 'Partnership Fees', ar: 'رسوم الشراكة' },
	'Amount Paid': { en: 'Amount Paid', ar: 'المبلغ المدفوع' },
	'Download Invoice': { en: 'Download Invoice', ar: 'تنزيل الفاتورة' },
	'Pay Now': { en: 'Pay Now', ar: 'ادفع الآن' },
	'Change Payment Method': { en: 'Change Payment Method', ar: 'تغيير طريقة الدفع' },
	'Your payment with the card ending <strong>{card}</strong> failed for this invoice due to the following reason:<div class="text-sm font-mono text-ink-gray-6 rounded p-2 bg-surface-gray-2">{error}</div><p class="text-base">Please change your payment method to pay this invoice.</p>': {
		en: 'Your payment with the card ending <strong>{card}</strong> failed for this invoice due to the following reason:<div class="text-sm font-mono text-ink-gray-6 rounded p-2 bg-surface-gray-2">{error}</div><p class="text-base">Please change your payment method to pay this invoice.</p>',
		ar: 'فشل الدفع ببطاقة تنتهي بـ <strong>{card}</strong> لهذه الفاتورة بسبب: <div class="text-sm font-mono text-ink-gray-6 rounded p-2 bg-surface-gray-2">{error}</div><p class="text-base">يُرجى تغيير طريقة الدفع لدفع هذه الفاتورة.</p>',
	},
	// PaymentDetails
	'Payment details': { en: 'Payment details', ar: 'تفاصيل الدفع' },
	'Active Card': { en: 'Active Card', ar: 'البطاقة النشطة' },
	'No card added': { en: 'No card added', ar: 'لم تتم إضافة بطاقة' },
	'Change card': { en: 'Change card', ar: 'تغيير البطاقة' },
	'Add card': { en: 'Add card', ar: 'إضافة بطاقة' },
	'Billing address': { en: 'Billing address', ar: 'عنوان الفوترة' },
	'No address': { en: 'No address', ar: 'لا يوجد عنوان' },
	'Add billing address': { en: 'Add billing address', ar: 'إضافة عنوان فوترة' },
	'Mode of payment': { en: 'Mode of payment', ar: 'طريقة الدفع' },
	'Not set': { en: 'Not set', ar: 'غير معين' },
	'Set mode': { en: 'Set mode', ar: 'تعيين الوضع' },
	'Credit balance': { en: 'Credit balance', ar: 'الرصيد المتبقي' },
	'Add credit': { en: 'Add credit', ar: 'إضافة رصيد' },
	'Budget Alerts': { en: 'Budget Alerts', ar: 'تنبيهات الميزانية' },
	'Set Budget Alert': { en: 'Set Budget Alert', ar: 'تعيين تنبيه الميزانية' },
	'Prepaid credits': { en: 'Prepaid credits', ar: 'رصيد مسبق الدفع' },
	'Paid by Partner': { en: 'Paid by Partner', ar: 'مدفوع من الشريك' },
	'Your card will be charged for monthly subscription': {
		en: 'Your card will be charged for monthly subscription',
		ar: 'سيتم خصم الاشتراك الشهري من بطاقتك',
	},
	'You will be charged from your credit balance for monthly subscription': {
		en: 'You will be charged from your credit balance for monthly subscription',
		ar: 'سيتم الخصم من رصيدك المتبقي للاشتراك الشهري',
	},
	'Your partner will be charged for monthly subscription': {
		en: 'Your partner will be charged for monthly subscription',
		ar: 'سيتم تحصيل الاشتراك الشهري من شريكك',
	},
	'Your UPI will be auto-debited for monthly subscription': {
		en: 'Your UPI will be auto-debited for monthly subscription',
		ar: 'سيتم الخصم التلقائي من UPI للاشتراك الشهري',
	},
	'Confirm Payment Mode': { en: 'Confirm Payment Mode', ar: 'تأكيد طريقة الدفع' },
	'By changing the payment mode to <strong>Paid by Partner</strong>, following details will be shared with your partner: <br><br><li>Site/Server name</li> <li>Plan name</li><li>Number of days site/server is active</li><br>Are you sure you want to proceed?': {
		en: 'By changing the payment mode to <strong>Paid by Partner</strong>, following details will be shared with your partner: <br><br><li>Site/Server name</li> <li>Plan name</li><li>Number of days site/server is active</li><br>Are you sure you want to proceed?',
		ar: 'بتغيير طريقة الدفع إلى <strong>مدفوع من الشريك</strong>، ستتم مشاركة التفاصيل التالية مع شريكك: <br><br><li>اسم الموقع/الخادم</li> <li>اسم الخطة</li><li>عدد أيام نشاط الموقع/الخادم</li><br>هل تريد بالتأكيد المتابعة؟',
	},
	'Change Payment Mode': { en: 'Change Payment Mode', ar: 'تغيير طريقة الدفع' },
	'Alternate Payment Methods': {
		en: 'Alternate Payment Methods',
		ar: 'طرق دفع بديلة',
	},
	'Multiple unpaid invoices': { en: 'Multiple unpaid invoices', ar: 'فواتير متعددة غير مدفوعة' },
	'You have multiple unpaid invoices. Please pay them from the invoices page': {
		en: 'You have multiple unpaid invoices. Please pay them from the invoices page',
		ar: 'لديك فواتير متعددة غير مدفوعة. يُرجى دفعها من صفحة الفواتير',
	},
	'Go to invoices': { en: 'Go to invoices', ar: 'الانتقال إلى الفواتير' },
	'Receive an email alert if monthly total exceeds limit set': {
		en: 'Receive an email alert if monthly total exceeds limit set',
		ar: 'تصلك رسالة تنبيه إذا تجاوز الإجمالي الشهري الحد المحدد',
	},
	// BillingPaymentMethods
	'No cards added.': { en: 'No cards added.', ar: 'لم تتم إضافة بطاقات.' },
	'Name on Card': { en: 'Name on Card', ar: 'الاسم على البطاقة' },
	'Default': { en: 'Default', ar: 'افتراضي' },
	'Expiry': { en: 'Expiry', ar: 'تاريخ الانتهاء' },
	'Mandated': { en: 'Mandated', ar: 'مفوض' },
	'The last payment failed on this card. Please use a different card.': {
		en: 'The last payment failed on this card. Please use a different card.',
		ar: 'فشل آخر دفع على هذه البطاقة. يُرجى استخدام بطاقة مختلفة.',
	},
	'Set as default': { en: 'Set as default', ar: 'تعيين كافتراضي' },
	'Setting as default...': {
		en: 'Setting as default...',
		ar: 'جاري التعيين كافتراضي...',
	},
	'Default card set': { en: 'Default card set', ar: 'تم تعيين البطاقة الافتراضية' },
	'Could not set default card': {
		en: 'Could not set default card',
		ar: 'تعذر تعيين البطاقة الافتراضية',
	},
	'Remove': { en: 'Remove', ar: 'إزالة' },
	'Cannot remove default card': {
		en: 'Cannot remove default card',
		ar: 'لا يمكن إزالة البطاقة الافتراضية',
	},
	'Remove Card': { en: 'Remove Card', ar: 'إزالة البطاقة' },
	'Are you sure you want to remove this card?': {
		en: 'Are you sure you want to remove this card?',
		ar: 'هل تريد بالتأكيد إزالة هذه البطاقة؟',
	},
	'Removing card...': { en: 'Removing card...', ar: 'جاري إزالة البطاقة...' },
	'Card removed': { en: 'Card removed', ar: 'تمت إزالة البطاقة' },
	'Could not remove card': { en: 'Could not remove card', ar: 'تعذرت إزالة البطاقة' },
	'Add Card': { en: 'Add Card', ar: 'إضافة بطاقة' },
	// BillingBalances + BillingForecast
	'Balance': { en: 'Balance', ar: 'الرصيد' },
	'Applied To Invoice {invoice}': {
		en: 'Applied to Invoice {invoice}',
		ar: 'تم تطبيقه على الفاتورة {invoice}',
	},
	'Month-To-Date Cost': {
		en: 'Month-To-Date Cost',
		ar: 'التكلفة حتى تاريخه من الشهر',
	},
	'Forecasted Month End Cost': {
		en: 'Forecasted Month End Cost',
		ar: 'تكلفة نهاية الشهر المتوقعة',
	},
	'Billing Comparison': { en: 'Billing Comparison', ar: 'مقارنة الفوترة' },
	'Time Period': { en: 'Time Period', ar: 'الفترة الزمنية' },
	'Month-To-Date Cost Breakdown': {
		en: 'Month-To-Date Cost Breakdown',
		ar: 'تفصيل التكلفة حتى تاريخه من الشهر',
	},
	'Amount ({symbol})': { en: 'Amount ({symbol})', ar: 'المبلغ ({symbol})' },
	'Last Month\n({month})': { en: 'Last Month\n({month})', ar: 'الشهر الماضي\n({month})' },
	'Month To Date\n({month})': { en: 'Month To Date\n({month})', ar: 'من بداية الشهر حتى تاريخه\n({month})' },
	'Forecast\n({month})': { en: 'Forecast\n({month})', ar: 'توقعات\n({month})' },
	'No usage data available for this month': {
		en: 'No usage data available for this month',
		ar: 'لا توجد بيانات استخدام لهذا الشهر',
	},
	// CardForm
	'Credit or Debit Card': { en: 'Credit or Debit Card', ar: 'بطاقة ائتمان أو خصم' },
	'We are attempting to charge your card with <strong>{amount}</strong> to make sure the card works. This amount will be <strong>refunded</strong> back to your account.': {
		en: 'We are attempting to charge your card with <strong>{amount}</strong> to make sure the card works. This amount will be <strong>refunded</strong> back to your account.',
		ar: 'نحاول خصم <strong>{amount}</strong> من بطاقتك للتأكد من أن البطاقة تعمل. سيتم <strong>استرداد</strong> هذا المبلغ إلى حسابك.',
	},
	'Verify & Save Card': { en: 'Verify & Save Card', ar: 'تحقق واحفظ البطاقة' },
	'Verifying Card': { en: 'Verifying Card', ar: 'جاري التحقق من البطاقة' },
	'Card Verified': { en: 'Card Verified', ar: 'تم التحقق من البطاقة' },
	'Card added successfully': { en: 'Card added successfully', ar: 'تمت إضافة البطاقة بنجاح' },
	'Your card was declined. It might be due to insufficient funds or you might\'ve exceeded your daily limit. Please try with another card or contact your bank.': {
		en: "Your card was declined. It might be due to insufficient funds or you might've exceeded your daily limit. Please try with another card or contact your bank.",
		ar: 'تم رفض بطاقتك. قد يكون السبب عدم كفاية الأموال أو تجاوز الحد اليومي. يُرجى تجربة بطاقة أخرى أو التواصل مع البنك.',
	},
	'Your card was declined. It might be due to restrictions on your card, like international transactions or online payments. Please try with another card or contact your bank.': {
		en: 'Your card was declined. It might be due to restrictions on your card, like international transactions or online payments. Please try with another card or contact your bank.',
		ar: 'تم رفض بطاقتك. قد يكون السبب قيوداً على بطاقتك، مثل المعاملات الدولية أو المدفوعات عبر الإنترنت. يُرجى تجربة بطاقة أخرى أو التواصل مع البنك.',
	},
	// PrepaidCreditsForm
	'Amount (Minimum Amount: {amount})': {
		en: 'Amount (Minimum Amount: {amount})',
		ar: 'المبلغ (الحد الأدنى: {amount})',
	},
	'Total Amount + GST ({gst}%)': { en: 'Total Amount + GST ({gst}%)', ar: 'إجمالي المبلغ + ضريبة السلع والخدمات ({gst}%)' },
	'Amount in KES (Exchange Rate: {rate} against 1 USD)': {
		en: 'Amount in KES (Exchange Rate: {rate} against 1 USD)',
		ar: 'المبلغ بشلن كيني (سعر الصرف: {rate} مقابل دولار واحد)',
	},
	// BuyCreditsStripe
	'Proceed to payment using Stripe': {
		en: 'Proceed to payment using Stripe',
		ar: 'المتابعة للدفع باستخدام Stripe',
	},
	'Make payment via Stripe': { en: 'Make payment via Stripe', ar: 'ادفع عبر Stripe' },
	'Amount must be greater than or equal to {amount}': {
		en: 'Amount must be greater than or equal to {amount}',
		ar: 'يجب أن يكون المبلغ أكبر من أو يساوي {amount}',
	},
	'Payment processed successfully, we will update your account shortly on confirmation from Stripe': {
		en: 'Payment processed successfully, we will update your account shortly on confirmation from Stripe',
		ar: 'تمت معالجة الدفع بنجاح، سنقوم بتحديث حسابك قريبًا بعد تأكيد Stripe',
	},
	// ChangeCardDialog
	'Choose active card': { en: 'Choose active card', ar: 'اختر البطاقة النشطة' },
	'Card ending in': { en: 'Card ending in', ar: 'بطاقة تنتهي بـ' },
	Expiry: { en: 'Expiry', ar: 'تاريخ الانتهاء' },
	'Add new card': { en: 'Add new card', ar: 'إضافة بطاقة جديدة' },
	'Default card set': { en: 'Default card set', ar: 'تم تعيين البطاقة الافتراضية' },
	'Could not set default card': {
		en: 'Could not set default card',
		ar: 'تعذر تعيين البطاقة الافتراضية',
	},
	'Could not remove card': { en: 'Could not remove card', ar: 'تعذرت إزالة البطاقة' },
	// BillingUPIAutopay
	'Setup UPI Autopay': { en: 'Setup UPI Autopay', ar: 'إعداد الدفع التلقائي عبر UPI' },
	'No UPI Autopay mandates set up.': {
		en: 'No UPI Autopay mandates set up.',
		ar: 'لا توجد تفويضات دفع تلقائي عبر UPI.',
	},
	'UPI ID': { en: 'UPI ID', ar: 'معرّف UPI' },
	'Max Amount': { en: 'Max Amount', ar: 'الحد الأقصى للمبلغ' },
	'Expires On': { en: 'Expires On', ar: 'تنتهي في' },
	'Cancel UPI Autopay': { en: 'Cancel UPI Autopay', ar: 'إلغاء الدفع التلقائي عبر UPI' },
	'Are you sure you want to cancel this UPI Autopay mandate?': {
		en: 'Are you sure you want to cancel this UPI Autopay mandate?',
		ar: 'هل أنت متأكد أنك تريد إلغاء تفويض الدفع التلقائي هذا عبر UPI؟',
	},
	'Setup Autopay': { en: 'Setup Autopay', ar: 'إعداد الدفع التلقائي' },
	'Mandate cancelled': { en: 'Mandate cancelled', ar: 'تم إلغاء التفويض' },
	'Could not cancel mandate': { en: 'Could not cancel mandate', ar: 'تعذر إلغاء التفويض' },
	'Opening payment window...': {
		en: 'Opening payment window...',
		ar: 'جاري فتح نافذة الدفع...',
	},
	// UPIAutopayForm
	'Simplify your billing by authorizing <strong>recurring monthly payments</strong> for your AlbannaTech invoices via Razorpay. Once set up, we’ll handle your future invoices automatically—no manual intervention required.': {
		en: 'Simplify your billing by authorizing <strong>recurring monthly payments</strong> for your AlbannaTech invoices via Razorpay. Once set up, we’ll handle your future invoices automatically—no manual intervention required.',
		ar: 'بسّط فوتورتك من خلال تفويض <strong>مدفوعات شهرية متكررة</strong> لفواتير AlbannaTech عبر Razorpay. بمجرد الإعداد، سنتعامل مع فواتيرك المستقبلية تلقائيًا—دون حاجة إلى تدخل يدوي.',
	},
	'Monthly Autopay Limit': { en: 'Monthly Autopay Limit', ar: 'حد الدفع التلقائي الشهري' },
	'Range: ₹500 - ₹1,00,000': { en: 'Range: ₹500 - ₹1,00,000', ar: 'النطاق: ₹500 - ₹1,00,000' },
	'<strong>Important:</strong> If an invoice exceeds this limit, the auto-debit will fail. Set this slightly higher than your typical bill to ensure uninterrupted service.': {
		en: '<strong>Important:</strong> If an invoice exceeds this limit, the auto-debit will fail. Set this slightly higher than your typical bill to ensure uninterrupted service.',
		ar: '<strong>مهم:</strong> إذا تجاوزت الفاتورة هذا الحد، فسيفشل الخصم التلقائي. اضبطه أعلى قليلًا من فاتورتك المعتادة لضمان خدمة دون انقطاع.',
	},
	'Enable Monthly Autopay': { en: 'Enable Monthly Autopay', ar: 'تفعيل الدفع التلقائي الشهري' },
	'Failed to create mandate': { en: 'Failed to create mandate', ar: 'تعذر إنشاء التفويض' },
	'UPI Autopay authorized successfully!': {
		en: 'UPI Autopay authorized successfully!',
		ar: 'تم التفويض بالدفع التلقائي عبر UPI بنجاح!',
	},
	'Failed to verify authorization': {
		en: 'Failed to verify authorization',
		ar: 'تعذر التحقق من التفويض',
	},
	'Maximum amount must be at least ₹500': {
		en: 'Maximum amount must be at least ₹500',
		ar: 'يجب ألا يقل الحد الأقصى للمبلغ عن ₹500',
	},
	'Maximum amount cannot exceed ₹1,00,000': {
		en: 'Maximum amount cannot exceed ₹1,00,000',
		ar: 'لا يمكن أن يتجاوز الحد الأقصى للمبلغ ₹1,00,000',
	},
	'UPI Autopay Authorization': { en: 'UPI Autopay Authorization', ar: 'تفويض الدفع التلقائي عبر UPI' },
	'Authorization cancelled': { en: 'Authorization cancelled', ar: 'تم إلغاء التفويض' },
	'Verifying authorization...': { en: 'Verifying authorization...', ar: 'جاري التحقق من التفويض...' },
	'Authorization failed': { en: 'Authorization failed', ar: 'فشل التفويض' },
	// BuyCreditsRazorpay
	'If you select Razorpay, you can pay using Credit Card, Debit Card, Net Banking, UPI, Wallets, etc. If you are using Net Banking, it may take upto 5 days for balance to reflect.': {
		en: 'If you select Razorpay, you can pay using Credit Card, Debit Card, Net Banking, UPI, Wallets, etc. If you are using Net Banking, it may take upto 5 days for balance to reflect.',
		ar: 'إذا اخترت Razorpay، يمكنك الدفع باستخدام بطاقة الائتمان أو بطاقة الخصم أو الصرافة الإلكترونية أو UPI أو المحافظ الإلكترونية، وغيرها. إذا كنت تستخدم الصرافة الإلكترونية، فقد يستغرق ظهور الرصيد حتى 5 أيام.',
	},
	'You can pay using your PayPal account. Processing may take a few minutes for the balance to reflect.': {
		en: 'You can pay using your PayPal account. Processing may take a few minutes for the balance to reflect.',
		ar: 'يمكنك الدفع باستخدام حساب PayPal. قد تستغرق المعالجة بضع دقائق لظهور الرصيد.',
	},
	'Loading payment gateway...': { en: 'Loading payment gateway...', ar: 'جاري تحميل بوابة الدفع...' },
	'Proceed to payment using {gateway}': {
		en: 'Proceed to payment using {gateway}',
		ar: 'المتابعة للدفع باستخدام {gateway}',
	},
	'Confirming payment': { en: 'Confirming payment', ar: 'جاري تأكيد الدفع' },
	'Failed to load payment gateway. Please refresh and try again.': {
		en: 'Failed to load payment gateway. Please refresh and try again.',
		ar: 'تعذر تحميل بوابة الدفع. يُرجى تحديث الصفحة والمحاولة مرة أخرى.',
	},
	'Amount should be equal to or greater than {amount}': {
		en: 'Amount should be equal to or greater than {amount}',
		ar: 'يجب أن يكون المبلغ مساويًا أو أكبر من {amount}',
	},
	'Payment failed': { en: 'Payment failed', ar: 'فشل الدفع' },
	'Payment successful': { en: 'Payment successful', ar: 'تم الدفع بنجاح' },
	'Pay using PayPal': { en: 'Pay using PayPal', ar: 'ادفع باستخدام PayPal' },
	// AddCardDialog & BillingDetailsDialog
	'Add at least one card before changing the payment mode.': {
		en: 'Add at least one card before changing the payment mode.',
		ar: 'أضف بطاقة واحدة على الأقل قبل تغيير طريقة الدفع.',
	},
	'Add billing details to your account before proceeding.': {
		en: 'Add billing details to your account before proceeding.',
		ar: 'أضف بيانات الفوترة إلى حسابك قبل المتابعة.',
	},
	// BuyPrepaidCreditsMpesa
	'Payment Partner': { en: 'Payment Partner', ar: 'شريك الدفع' },
	'Select Payment Partner': { en: 'Select Payment Partner', ar: 'اختر شريك الدفع' },
	'M-Pesa Phone Number': { en: 'M-Pesa Phone Number', ar: 'رقم هاتف M-Pesa' },
	'Tax ID': { en: 'Tax ID', ar: 'الرقم الضريبي' },
	'Tax(%)': { en: 'Tax(%)', ar: 'الضريبة (%)' },
	'Total Amount With Tax': { en: 'Total Amount With Tax', ar: 'إجمالي المبلغ مع الضريبة' },
	'Make payment via M-Pesa': { en: 'Make payment via M-Pesa', ar: 'ادفع عبر M-Pesa' },
	'Amount is less than the minimum allowed: {amount}': {
		en: 'Amount is less than the minimum allowed: {amount}',
		ar: 'المبلغ أقل من الحد الأدنى المسموح: {amount}',
	},
	'Amount is more than the maximum allowed: {amount}': {
		en: 'Amount is more than the maximum allowed: {amount}',
		ar: 'المبلغ أعلى من الحد الأقصى المسموح: {amount}',
	},
	'Both partner and phone number are required for payment.': {
		en: 'Both partner and phone number are required for payment.',
		ar: 'كلا من الشريك ورقم الهاتف مطلوبان لإتمام الدفع.',
	},
	'Tax ID is required for payment.': {
		en: 'Tax ID is required for payment.',
		ar: 'الرقم الضريبي مطلوب لإتمام الدفع.',
	},
	'Invalid Tax Id': { en: 'Invalid Tax Id', ar: 'رقم ضريبي غير صالح' },
	'Please follow the instructions on your phone': {
		en: 'Please follow the instructions on your phone',
		ar: 'يُرجى اتباع التعليمات على هاتفك',
	},
	'Something went wrong. Please try again.': {
		en: 'Something went wrong. Please try again.',
		ar: 'حدث خطأ ما. يُرجى المحاولة مرة أخرى.',
	},
	'Payment Initiated successfully, check your phone for instructions': {
		en: 'Payment Initiated successfully, check your phone for instructions',
		ar: 'تم بدء الدفع بنجاح، تحقق من هاتفك للحصول على التعليمات',
	},
	'Payment failed. Please try again.': {
		en: 'Payment failed. Please try again.',
		ar: 'فشل الدفع. يُرجى المحاولة مرة أخرى.',
	},
	// BillingSummary
	'Recurring Charges': { en: 'Recurring Charges', ar: 'الرسوم المتكررة' },
	'Next charge date — {date}': {
		en: 'Next charge date — {date}',
		ar: 'تاريخ الخصم القادم — {date}',
	},
	'Your UPI will be auto-debited at the end of the billing cycle. Payment may take up to 24 hours to reflect after debit is initiated.': {
		en: 'Your UPI will be auto-debited at the end of the billing cycle. Payment may take up to 24 hours to reflect after debit is initiated.',
		ar: 'سيتم خصم UPI تلقائيًا في نهاية دورة الفوترة. قد يستغرق ظهور الدفع حتى 24 ساعة بعد بدء الخصم.',
	},
	'Current billing amount so far': { en: 'Current billing amount so far', ar: 'إجمالي الفوترة حتى الآن' },
	'Unpaid amount is': { en: 'Unpaid amount is', ar: 'المبلغ غير المدفوع هو' },
	'View Invoice': { en: 'View Invoice', ar: 'عرض الفاتورة' },
	'Pay now': { en: 'Pay now', ar: 'ادفع الآن' },
	// UpcomingInvoiceDialog
	'Total usage for this month': { en: 'Total usage for this month', ar: 'إجمالي الاستخدام لهذا الشهر' },
	// FinalizeInvoicesDialog
	'Finalize Unsettled Invoices': {
		en: 'Finalize Unsettled Invoices',
		ar: 'تسوية الفواتير غير المدفوعة',
	},
	'You have unpaid invoices on your account for the following periods:': {
		en: 'You have unpaid invoices on your account for the following periods:',
		ar: 'لديك فواتير غير مدفوعة على حسابك للفترات التالية:',
	},
	'Please finalize and settle them before removing all payment methods, switching to Paid by Partner method or disabling the account. You can check the details of invoices and make the payment from': {
		en: 'Please finalize and settle them before removing all payment methods, switching to Paid by Partner method or disabling the account. You can check the details of invoices and make the payment from',
		ar: 'يُرجى تسويتها وسدادها قبل إزالة جميع طرق الدفع، أو التبديل إلى طريقة الدفع بواسطة الشريك، أو تعطيل الحساب. يمكنك الاطلاع على تفاصيل الفواتير وإتمام الدفع من',
	},
	here: { en: 'here', ar: 'هنا' },
	'It might take up to 2 hours for the payment to reflect against your invoices.': {
		en: 'It might take up to 2 hours for the payment to reflect against your invoices.',
		ar: 'قد يستغرق ظهور الدفع مقابل فواتيرك حتى ساعتين.',
	},
	'Finalize Invoices': { en: 'Finalize Invoices', ar: 'تسوية الفواتير' },
	'Invoices finalized successfully': {
		en: 'Invoices finalized successfully',
		ar: 'تمت تسوية الفواتير بنجاح',
	},
	// AddPrepaidCreditsDialog
	'Add Credit Balance': { en: 'Add Credit Balance', ar: 'إضافة رصيد' },
	'Add credits to your account before changing the payment mode.': {
		en: 'Add credits to your account before changing the payment mode.',
		ar: 'أضف رصيدًا إلى حسابك قبل تغيير طريقة الدفع.',
	},
	// BudgetAlertDialog
	'Enable Budget Alerts': { en: 'Enable Budget Alerts', ar: 'تفعيل تنبيهات الميزانية' },
	'Receive an email alert when monthly spend exceeds limit': {
		en: 'Receive an email alert when monthly spend exceeds limit',
		ar: 'استلم تنبيهًا بالبريد الإلكتروني عند تجاوز الإنفاق الشهري للحد المحدد',
	},
	'Monthly Alert Limit ({currency})': {
		en: 'Monthly Alert Limit ({currency})',
		ar: 'حد التنبيه الشهري ({currency})',
	},
	'Enter amount in {currency}': { en: 'Enter amount in {currency}', ar: 'أدخل المبلغ بـ {currency}' },
	'Please enter a valid positive amount': {
		en: 'Please enter a valid amount',
		ar: 'يُرجى إدخال مبلغ صحيح موجب',
	},
	'An error occurred while saving settings. Please try again.': {
		en: 'An error occurred while saving settings. Please try again.',
		ar: 'حدث خطأ أثناء حفظ الإعدادات. يُرجى المحاولة مرة أخرى.',
	},
	// BillingDetails
	'Billing Name': { en: 'Billing Name', ar: 'اسم الفوترة' },
	'Update billing details': { en: 'Update billing details', ar: 'تحديث بيانات الفوترة' },
	'Billing Name is required': { en: 'Billing Name is required', ar: 'اسم الفوترة مطلوب' },
	'Billing Name contains invalid characters': {
		en: 'Billing Name contains invalid characters',
		ar: 'اسم الفوترة يحتوي على أحرف غير صالحة',
	},
	// NewAddressForm
	'I have GSTIN': { en: 'I have GSTIN', ar: 'لدي رقم GSTIN' },
	'Billing information updated': {
		en: 'Billing information updated',
		ar: 'تم تحديث معلومات الفوترة',
	},
	'{label} is required': { en: '{label} is required', ar: '{label} مطلوب' },
	'State / Province / Region': {
		en: 'State / Province / Region',
		ar: 'الولاية / المقاطعة / المنطقة',
	},
};

export default billing;
