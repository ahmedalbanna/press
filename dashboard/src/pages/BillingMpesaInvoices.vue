<template>
	<div class="p-5">
		<ObjectList :options="options" />
	</div>
</template>

<script>
import { frappeRequest } from 'frappe-ui';
import ObjectList from '../components/ObjectList.vue';
import { icon } from '../utils/components';
import { t } from '../utils/language';

export default {
	name: 'BillingMpesaInvoices',
	data() {
		return {
			invoices: [],
			loading: false,
			errorMessage: null,
		};
	},
	components: {
		ObjectList,
	},
	methods: {
		async fetchInvoices() {
			this.loading = true;
			try {
				const response = await frappeRequest({
					url: '/api/method/press.api.regional_payments.mpesa.utils.display_invoices_by_partner',
					method: 'GET',
				});
				this.invoices = response;
			} catch (error) {
				this.errorMessage = `Failed to load invoices. ${error}`;
			} finally {
				this.loading = false;
			}
		},
		formatCurrency(value) {
			return new Intl.NumberFormat('en-US', {
				style: 'currency',
				currency: 'Ksh',
			}).format(value);
		},
	},
	computed: {
		options() {
			return {
				doctype: 'Mpesa Payment Record',
				fields: [
					'name',
					'posting_date',
					'amount',
					'local_invoice',
					'payment_partner',
					'amount_usd',
					'exchange_rate',
				],
				columns: [
					{
						label: t('Invoice Name'),
						fieldname: 'name',
						width: 1,
					},
					{
						label: t('Date'),
						fieldname: 'posting_date',
						width: 0.7,
					},
					{
						label: t('Amount'),
						fieldname: 'amount',
						align: 'center',
						width: 0.6,
					},
					{
						label: t('Amount (USD)'),
						fieldname: 'amount_usd',
						align: 'center',
						width: 0.6,
					},
					{
						label: t('Exchange Rate'),
						fieldname: 'exchange_rate',
						align: 'center',
						width: 0.6,
					},
					{
						label: t('Payment Partner'),
						fieldname: 'payment_partner',
					},
					{
						label: '',
						type: 'Button',
						align: 'right',
						Button: ({ row }) => {
							if (row.local_invoice) {
								return {
									label: t('Download Invoice'),
									slots: {
										prefix: icon('download'),
									},
									onClick: () => {
										window.open(row.local_invoice);
									},
								};
							}
						},
					},
				],
				orderBy: 'posting_date desc',
			};
		},
	},
	mounted() {
		this.fetchInvoices();
	},
};
</script>
