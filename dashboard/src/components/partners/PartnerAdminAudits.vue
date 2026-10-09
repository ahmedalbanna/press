<template>
	<div class="p-5">
		<ObjectList :options="partnerAuditsList" />
	</div>
</template>
<script>
import ObjectList from '../ObjectList.vue';
import { t } from '../../utils/language'

export default {
	name: 'PartnerAdminAudits',
	components: {
		ObjectList,
	},
	computed: {
		partnerAuditsList() {
			return {
				doctype: 'Partner Audit',
				fields: [
					'mode_of_audit',
					'status',
					'proposed_audit_date',
					'audit_date',
				],
				columns: [
					{
						label: t('Partner'),
						fieldname: 'partner_team',
						width: 0.8,
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
						width: 0.5,
					},
					{
						label: t('Audit Type'),
						fieldname: 'mode_of_audit',
						width: 0.5,
					},
					{
						label: t('Conducted By'),
						fieldname: 'conducted_by',
						width: 0.8,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('NC Count'),
						fieldname: 'non_conformance_count',
						width: 0.4,
						type: 'Badge',
						align: 'center',
					},
					{
						label: t('Requested Date'),
						fieldname: 'proposed_audit_date',
						width: 0.8,
						format(value) {
							if (!value) return '';
							return Intl.DateTimeFormat('en-US', {
								year: 'numeric',
								month: 'long',
								day: 'numeric',
							}).format(new Date(value));
						},
					},
					{
						label: t('Audit Date'),
						fieldname: 'audit_date',
						width: 0.8,
						format(value) {
							if (!value) return '';
							return Intl.DateTimeFormat('en-US', {
								year: 'numeric',
								month: 'long',
								day: 'numeric',
							}).format(new Date(value));
						},
					},
				],
				filterControls() {
					return [
						{
							type: 'date',
							fieldname: 'proposed_audit_date',
							label: t('Audit Date'),
						},
						{
							type: 'select',
							fieldname: 'status',
							label: t('Status'),
							options: [
								{ label: t('All'), value: 'All' },
								{ label: t('Requested'), value: 'Requested' },
								{ label: t('Scheduled'), value: 'Scheduled' },
								{ label: t('In Progress'), value: 'In Progress' },
								{ label: t('Completed'), value: 'Completed' },
								{ label: t('On Hold'), value: 'On Hold' },
								{ label: t('Cancelled'), value: 'Cancelled' },
							],
						},
						{
							type: 'select',
							fieldname: 'mode_of_audit',
							label: t('Audit Type'),
							options: [
								{ label: t('All'), value: 'All' },
								{ label: t('In-Person'), value: 'In-Person' },
								{ label: t('Online'), value: 'Online' },
								{ label: t('Hybrid'), value: 'Hybrid' },
							],
						},
					];
				},
				onRowClick: (row) => {
					this.$router.push({
						name: 'PartnerNCList',
						params: { partner_audit: row.name },
					});
				},
			};
		},
	},
};
</script>
