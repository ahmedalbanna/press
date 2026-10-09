<template>
	<div>
		<ObjectList :options="options" />
	</div>
</template>
<script>
import ObjectList from '../ObjectList.vue';
import { currency } from '../../utils/format';
import dayjs from '../../utils/dayjs';
import { t } from '../../utils/language'

export default {
	name: 'PartnerCustomerInvoices',
	props: ['customerTeam', 'customerCurrency'],
	components: {
		ObjectList,
	},
	data() {
		return {
			team: this.customerTeam,
			currency: this.customerCurrency,
		};
	},
	computed: {
		options() {
			return {
				doctype: 'Invoice',
				fields: ['type'],
				columns: [
					{ label: t('Invoice'), fieldname: 'name' },
					{ label: t('Status'), fieldname: 'status', type: 'Badge' },
					{
						label: t('Date'),
						fieldname: 'due_date',
						format(value) {
							return Intl.DateTimeFormat('en-US', {
								year: 'numeric',
								month: 'short',
								day: 'numeric',
							}).format(new Date(value));
						},
					},
					{ label: t('Total'), fieldname: 'total', format: this.formatCurrency },
					{
						label: t('Amount Due'),
						fieldname: 'amount_due',
						format: this.formatCurrency,
					},
				],
				filters: {
					team: this.team,
					due_date: [
						'>=',
						dayjs().subtract(5, 'month').endOf('month').format('YYYY-MM-DD'),
					],
					partner_customer: true,
				},
			};
		},
	},
	methods: {
		formatCurrency(value) {
			if (value === 0) {
				return '';
			}
			return currency(value, this.currency);
		},
	},
};
</script>
