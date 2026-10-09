<template>
	<div class="px-2">
		<GenericList :options="partnerContributionsList" />
	</div>
</template>
<script>
import GenericList from '../GenericList.vue';
import { currency, userCurrency } from '../../utils/format';
import { t } from '../../utils/language'
export default {
	name: 'PartnerContribution',
	props: ['partnerEmail'],
	components: {
		GenericList,
	},
	data() {
		return {
			partnerContributions: [],
		};
	},
	resources: {
		getPartnerContribution() {
			return {
				url: 'press.api.partner.get_partner_contribution_list',
				auto: true,
				params: {
					partner_email: this.partnerEmail,
				},
				onSuccess(data) {
					this.partnerContributions = data.map((d) => {
						return {
							customer_name: d.customer_name,
							status: d.status,
							due_date: d.due_date,
							currency: d.currency,
							total: d.total_before_discount,
							partner_total: d.partner_total,
						};
					});
				},
			};
		},
	},
	computed: {
		partnerContributionsList() {
			return {
				data: this.partnerContributions,
				selectable: false,
				columns: [
					{
						label: t('Customer'),
						fieldname: 'customer_name',
					},
					{
						label: t('Status'),
						fieldname: 'status',
						width: 0.5,
					},
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
						width: 0.6,
					},
					{
						label: t('Currency'),
						fieldname: 'currency',
						width: 0.5,
						align: 'center',
					},
					{
						label: t('Total'),
						fieldname: 'total',
						format(value, columns) {
							if (value === 0) {
								return '';
							}
							return currency(value, columns.currency);
						},
						align: 'right',
						width: 0.6,
					},
					{
						label: t('Partner Total'),
						fieldname: 'partner_total',
						format(value) {
							return userCurrency(value);
						},
						align: 'right',
						width: 0.6,
					},
				],
			};
		},
	},
};
</script>
