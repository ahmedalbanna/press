<template>
	<div class="p-5">
		<ObjectList :options="partnerAdminLeadsList" />
	</div>
</template>
<script>
import ObjectList from '../components/ObjectList.vue';
import { t } from '../utils/language'
export default {
	name: 'PartnerAdminLeads',
	components: {
		ObjectList,
	},
	resources: {
		leadOwners() {
			return {
				url: 'press.api.partner.get_lead_owners',
				auto: true,
				initialData: [],
			};
		},
	},
	computed: {
		partnerAdminLeadsList() {
			let leadOwners = this.$resources.leadOwners.data || [];
			return {
				doctype: 'Partner Lead',
				columns: [
					{
						label: t('Lead Name'),
						fieldname: 'lead_name',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Organization'),
						fieldname: 'organization_name',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Source'),
						fieldname: 'lead_source',
						width: 0.5,
					},
					{
						label: t('Partner'),
						fieldname: 'company_name',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Status'),
						fieldname: 'status',
						type: 'Badge',
						width: 0.4,
						align: 'center',
					},
					{
						label: t('Lead ID'),
						fieldname: 'name',
						width: 0.4,
					},
				],
				filterControls() {
					return [
						{
							type: 'data',
							fieldname: 'search-text',
							label: t('Search for org, lead or partner'),
						},
						{
							type: 'select',
							fieldname: 'source',
							label: t('Source'),
							options: [
								{ label: t('All'), value: 'All' },
								{ label: t('Partner Owned'), value: 'Partner Owned' },
								{ label: t('Passed to Partner'), value: 'Passed to Partner' },
								{ label: t('Partner Listing'), value: 'Partner Listing' },
							],
						},
						{
							type: 'select',
							fieldname: 'status',
							label: t('Status'),
							options: [
								{ label: t('All'), value: 'All' },
								{ label: t('Open'), value: 'Open' },
								{ label: t('Qualification'), value: 'Qualification' },
								{ label: t('Demo/Making'), value: 'Demo/Making' },
								{ label: t('Follow Up'), value: 'Follow Up' },
								{ label: t('Proposal/Quotation'), value: 'Proposal/Quotation' },
								{ label: t('Negotiation'), value: 'Negotiation' },
								{ label: t('Ready to Close'), value: 'Ready to Close' },
								{ label: t('In Process'), value: 'In Process' },
								{ label: t('Won'), value: 'Won' },
								{ label: t('Lost'), value: 'Lost' },
								{ label: t('Junk'), value: 'Junk' },
								{ label: t('Closed'), value: 'Closed' },
							],
						},
						{
							type: 'select',
							fieldname: 'lead_owner',
							label: t('Lead Owner'),
							options: [
								{ label: t('All'), value: 'All' },
								...leadOwners.map((owner) => ({
									label: owner.label,
									value: owner.value,
								})),
							],
						},
						{
							type: 'checkbox',
							fieldname: 'is_starter_pack',
							label: t('Starter Pack'),
						},
					];
				},
				onRowClick: (row) => {
					this.$router.push({
						name: 'LeadOverview',
						params: { leadId: row.name },
					});
				},
			};
		},
	},
};
</script>
