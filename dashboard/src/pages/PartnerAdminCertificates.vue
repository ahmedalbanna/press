<template>
	<div class="p-5">
		<ObjectList :options="partnerCertificatesList" />
	</div>
</template>

<script>
import { h } from 'vue';
import { FeatherIcon, Tooltip } from 'frappe-ui';
import { icon } from '../utils/components';
import ObjectList from '../components/ObjectList.vue';
import { t } from '../utils/language'
export default {
	name: 'PartnerAdminCertificates',
	components: {
		ObjectList,
	},
	computed: {
		partnerCertificatesList() {
			return {
				doctype: 'Partner Certificate',
				fields: ['free', 'certificate_link'],
				columns: [
					{
						label: t('Member Name'),
						fieldname: 'partner_member_name',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Member Email'),
						fieldname: 'partner_member_email',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Issued On'),
						fieldname: 'issue_date',
						width: 0.5,
						format(value) {
							return Intl.DateTimeFormat('en-US', {
								year: 'numeric',
								month: 'long',
								day: 'numeric',
							}).format(new Date(value));
						},
					},
					{
						label: t('Course'),
						fieldname: 'course',
						format(value) {
							return value == 'frappe-developer-certification'
								? 'Framework'
								: 'ERPNext';
						},
						width: 0.5,
					},
					{
						label: t('Partner'),
						fieldname: 'team',
						width: 0.6,
						class: 'truncate',
						format: (value) => {
							if (!value) return '';
							return value.length > 25 ? `${value.slice(0, 25)}...` : value;
						},
					},
					{
						label: t('Version'),
						fieldname: 'version',
						width: 0.3,
						align: 'center',
					},
					{
						label: t('Free'),
						fieldname: 'free',
						type: 'Component',
						align: 'center',
						width: 0.3,
						component({ row }) {
							if (row.free) {
								return h(
									Tooltip,
									{
										text: t('Free Certification'),
									},
									() =>
										h(FeatherIcon, {
											name: 'check-circle',
											class: 'h-4 w-4 text-green-600',
										}),
								);
							}
						},
					},
					{
						label: t('Certificate Link'),
						type: 'Button',
						align: 'center',
						width: 0.5,
						Button({ row }) {
							return {
								label: t('View'),
								slots: {
									prefix: icon('external-link'),
								},
								onClick: (e) => {
									e.stopPropagation();
									window.open(row.certificate_link);
								},
							};
						},
					},
				],
				filterControls() {
					return [
						{
							type: 'data',
							fieldname: 'search-text',
							label: t('Search'),
						},
						{
							type: 'select',
							fieldname: 'course',
							label: t('Course'),
							options: [
								{ label: t('Framework'), value: 'frappe-developer-certification' },
								{ label: t('ERPNext'), value: 'erpnext-distribution' },
							],
						},
					];
				},
				orderBy: 'creation desc',
			};
		},
	},
};
</script>
