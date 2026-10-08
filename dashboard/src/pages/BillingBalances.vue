<template>
	<div class="p-5">
		<ObjectList :options="options" />
	</div>
</template>
<script>
import ObjectList from '../components/ObjectList.vue';
import { t, tr } from '../utils/language';
export default {
	name: 'BillingBalances',
	props: ['tab'],
	components: {
		ObjectList,
	},
	computed: {
		options() {
			return {
				doctype: 'Balance Transaction',
				fields: ['type', 'source', 'invoice'],
				columns: [
					{
						label: t('Date'),
						fieldname: 'creation',
						format(value) {
							return Intl.DateTimeFormat('en-US', {
								year: 'numeric',
								month: 'long',
								day: 'numeric',
							}).format(new Date(value));
						},
					},
					{
						label: t('Description'),
						format(value, row) {
							if (row.type === 'Applied To Invoice' && row.invoice) {
								return tr('Applied to Invoice {invoice}', { invoice: row.invoice });
							}

							return row.amount < 0 ? row.type : row.source;
						},
					},
					{
						label: t('Amount'),
						fieldname: 'amount',
						align: 'right',
						format: this.formatCurrency,
					},
					{
						label: t('Balance'),
						fieldname: 'ending_balance',
						align: 'right',
						format: this.formatCurrency,
					},
				],
				filters: {
					docstatus: 1,
					team: this.$team.name,
				},
				orderBy: 'creation desc',
			};
		},
	},
	methods: {
		formatCurrency(value) {
			if (value === 0) {
				return '';
			}
			return this.$format.userCurrency(value);
		},
	},
};
</script>
