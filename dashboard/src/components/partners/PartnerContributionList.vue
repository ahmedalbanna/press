<template>
	<div class="p-4">
		<ObjectList :options="partnerInvoices" />
		<Dialog
			v-model="invoiceDialog"
			:options="{
				size: '4xl',
				title: 'Invoice Details',
			}"
		>
			<template #body-content>
				<template v-if="showInvoice">
					<div
						v-if="showInvoice.status === 'Empty'"
						class="text-base text-ink-gray-6"
					>
						{{ t('Nothing to show') }}
					</div>
					<InvoiceDetail v-else :invoiceId="showInvoice.name" />
				</template>
			</template>
		</Dialog>
	</div>
</template>
<script setup>
import ObjectList from '../ObjectList.vue';
import { computed, ref } from 'vue';
import InvoiceDetail from './InvoiceDetail.vue';
import { currency } from '../../utils/format';
import { t } from '../../utils/language'

let showInvoice = ref(null);
const invoiceDialog = ref(false);
const partnerInvoices = computed(() => {
	return {
		resource() {
			return {
				url: 'press.api.partner.get_partner_invoices',
				auto: true,
				initialData: [],
				transform(data) {
					return data.map((d) => {
						return {
							name: d.name,
							customer_name: d.customer_name,
							due_date: d.due_date || '',
							total_before_discount: d.total_before_discount || '',
							currency: d.currency || '',
							status: d.status || '',
						};
					});
				},
			};
		},
		columns: [
			{
				label: t('Customer Name'),
				fieldname: 'customer_name',
			},
			{
				label: t('Date'),
				fieldname: 'due_date',
				format(value) {
					if (!value) {
						return '';
					}
					return Intl.DateTimeFormat('en-US', {
						year: 'numeric',
						month: 'short',
						day: 'numeric',
					}).format(new Date(value));
				},
				align: 'center',
			},
			{
				label: t('Invoice ID'),
				fieldname: 'name',
				align: 'center',
			},
			{
				label: t('Status'),
				fieldname: 'status',
				type: 'Badge',
				align: 'center',
			},
			{
				label: t('Currency'),
				fieldname: 'currency',
				align: 'center',
			},
			{
				label: t('Amount'),
				fieldname: 'total_before_discount',
				align: 'right',
				format(value, row) {
					return currency(value, row.currency);
				},
			},
		],
		filterControls() {
			return [
				{
					type: 'select',
					fieldname: 'status',
					label: t('Status'),
					options: ['', 'Draft', 'Unpaid', 'Paid'],
				},
				{
					type: 'date',
					fieldname: 'due_date',
					label: t('Due Date'),
				},
			];
		},
		orderBy: 'creation desc',
		onRowClick(row) {
			showInvoice = row;
			invoiceDialog.value = true;
		},
	};
});
</script>
