<template>
	<div class="p-5">
		<ObjectList :options="partnerAuditsList" />
	</div>
</template>
<script setup>
import { computed, inject, h } from 'vue';
import ObjectList from '../ObjectList.vue';
import { icon, renderDialog } from '../../utils/components';
import router from '../../router';
import NewPartnerAudit from './NewPartnerAudit.vue';
import { t } from '../../utils/language'

const team = inject('team');

const partnerAuditsList = computed(() => {
	return {
		doctype: 'Partner Audit',
		fields: ['mode_of_audit', 'status', 'proposed_audit_date', 'audit_date'],
		filters: {
			team: team.doc.name,
		},
		columns: [
			{
				label: t('Audit Type'),
				fieldname: 'mode_of_audit',
			},
			{
				label: t('Status'),
				fieldname: 'status',
				type: 'Badge',
			},
			{
				label: t('Conducted By'),
				fieldname: 'conducted_by',
			},
			{
				label: t('NC Count'),
				fieldname: 'non_conformance_count',
				type: 'Badge',
				align: 'center',
			},
			{
				label: t('Requested Date'),
				fieldname: 'proposed_audit_date',
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
			];
		},
		actions() {
			return [
				{
					label: t('Request for Audit'),
					slots: {
						prefix: icon('plus'),
					},
					onClick: () => {
						return renderDialog(
							h(NewPartnerAudit, {
								modelValue: true,
							}),
						);
					},
				},
			];
		},
		onRowClick: (row) => {
			router.push({
				name: 'PartnerNCList',
				params: { partner_audit: row.name },
			});
		},
	};
});
</script>
