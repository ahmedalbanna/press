<template>
	<div class="p-4">
		<ObjectList :options="partnerTeams" />
	</div>
</template>
<script>
import ObjectList from '../components/ObjectList.vue';
import { t } from '../utils/language'
export default {
	name: 'PartnerList',
	components: {
		ObjectList,
	},
	data() {
		return {};
	},
	computed: {
		partnerTeams() {
			return {
				resource() {
					return {
						url: 'press.api.partner.get_partner_teams',
						transform(data) {
							return data.map((d) => {
								return {
									company: d.company_name,
									email: d.partner_email,
									country: d.country,
									tier: d.partner_tier || '',
								};
							});
						},
						initialData: [],
						auto: true,
					};
				},
				columns: [
					{
						label: t('Company'),
						fieldname: 'company',
					},
					{
						label: t('Partner Email'),
						fieldname: 'email',
						width: 0.8,
					},
					{
						label: t('Country'),
						fieldname: 'country',
						width: 0.5,
					},
					{
						label: t('Tier'),
						fieldname: 'tier',
						width: 0.5,
					},
				],
				onRowClick(row) {
					console.log('clicked', row);
				},
				filterControls() {
					return [
						{
							type: 'data',
							label: t('Partner'),
							fieldname: 'company',
						},
						{
							type: 'data',
							label: t('Partner Email'),
							fieldname: 'email',
						},
						{
							type: 'data',
							label: t('Country'),
							fieldname: 'country',
						},
						{
							type: 'select',
							label: t('Tier'),
							fieldname: 'tier',
							options: ['', 'Entry', 'Emerging', 'Bronze', 'Silver', 'Gold'],
						},
						{
							type: 'checkbox',
							label: t('Active Partners'),
							fieldname: 'active_only',
						},
					];
				},
			};
		},
	},
};
</script>
