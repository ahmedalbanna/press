<template>
	<div>
		<div
			v-if="
				lead && (lead.partner_team == $team.doc.name || $team.doc.is_desk_user)
			"
		>
			<div
				class="flex flex-col gap-5 overflow-y-auto px-4 py-6 sm:px-10 lg:px-60"
			>
				<div class="flex flex-wrap items-center justify-between gap-3">
					<div class="flex flex-wrap items-center gap-3">
						<h1 class="text-xl font-semibold sm:text-3xl">
							{{ lead?.organization_name }}
						</h1>
						<Badge
							variant="subtle"
							:theme="themeMap[lead?.status]"
							size="lg"
							:label="lead?.status"
						/>
					</div>
					<div class="shrink-0">
						<Dropdown :options="statusOptions">
							<template #default="{ open }">
								<Button :label="lead?.status || 'Status'" variant="solid">
									<template #suffix>
										<FeatherIcon
											:name="open ? 'chevron-up' : 'chevron-down'"
											class="h-4"
										/>
									</template>
								</Button>
							</template>
						</Dropdown>
					</div>
				</div>
				<div class="rounded-lg text-base text-ink-gray-9 border">
					<div class="p-4">
						<div class="flex items-center justify-between pb-2">
							<div class="font-semibold text-lg sm:text-xl">{{ t('Company Information') }}</div>
							<Button
								variant="subtle"
								@click="
									() => {
										showLeadDetailsDialog = true;
									}
								"
							>
								{{ t('Edit') }}
							</Button>
						</div>
						<div class="my-1 h-px bg-surface-gray-2" />
						<div class="pt-2">
							<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
								<div v-for="item in company_info" class="flex-1">
									<div class="text-sm text-ink-gray-6">
										{{ item.label }}
									</div>
									<div
										v-if="item.label === 'Plan Type' && item.value"
										class="py-1"
									>
										<Badge
											variant="outline"
											theme="blue"
											size="lg"
											:label="t('Starter Pack')"
										/>
									</div>
									<div v-else class="text-base font-medium py-2 sm:text-lg">
										{{ item.value || '-' }}
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div class="rounded-lg text-base text-ink-gray-9 border">
					<div class="p-4">
						<div class="flex items-center justify-between pb-2">
							<div class="font-semibold text-lg sm:text-xl">{{ t('Contact Info') }}</div>
						</div>
						<div class="my-1 h-px bg-surface-gray-2" />
						<div class="pt-2">
							<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
								<div v-for="item in contact_info" class="flex-1">
									<div class="text-sm text-ink-gray-6">
										{{ item.label }}
									</div>
									<div class="text-base font-medium py-2 sm:text-lg">
										{{ item.value || '-' }}
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div class="rounded-lg text-base text-ink-gray-9 border">
					<div class="p-4">
						<div class="flex items-center justify-between pb-2">
							<div class="font-semibold text-lg sm:text-xl">{{ t('Deal Info') }}</div>
						</div>
						<div class="my-1 h-px bg-surface-gray-2" />
						<div class="pt-2">
							<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
								<div v-for="item in deal_info" class="flex-1">
									<div class="text-sm text-ink-gray-6">
										{{ item.label }}
									</div>
									<div v-if="item.label === 'Probability'" class="py-1">
										<Badge
											variant="outline"
											:theme="probabilityTheme[item.value]"
											size="lg"
											:label="item.value"
										/>
									</div>
									<div v-else class="text-base font-medium py-2 sm:text-lg">
										{{ item.value || '-' }}
									</div>
								</div>
							</div>
							<!-- <div class="my-1 h-px bg-surface-gray-2" /> -->
							<div class="pt-2">
								<div class="text-sm text-ink-gray-6">{{ t('Requirement') }}</div>
								<div class="text-base leading-6 font-normal py-2">
									<div v-html="lead?.requirement"></div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			<LeadDetailsDialog
				v-if="showLeadDetailsDialog"
				v-model="showLeadDetailsDialog"
				@success="
					() => {
						$resources.lead.reload();
						showLeadDetailsDialog = false;
					}
				"
			/>
			<UpdateEngagementStageDialog
				v-if="showUpdateEngagementStageDialog"
				v-model="showUpdateEngagementStageDialog"
				:lead_id="lead.name"
				:status="status"
				@update="
					() => {
						$resources.lead.reload();
						showUpdateEngagementStageDialog = false;
					}
				"
			/>
			<UpdateWonDialog
				v-if="showUpdateWonDialog"
				v-model="showUpdateWonDialog"
				:lead_id="lead.name"
				@update="
					() => {
						$resources.lead.reload();
						showUpdateWonDialog = false;
					}
				"
			/>
			<UpdateLostDialog
				v-if="showUpdateLostDialog"
				v-model="showUpdateLostDialog"
				:lead_id="lead.name"
				@update="
					() => {
						$resources.lead.reload();
						showUpdateLostDialog = false;
					}
				"
			/>
		</div>
		<div
			v-else
			class="mx-auto mt-60 w-fit rounded border border-dashed px-12 py-8 text-center text-ink-gray-6"
		>
			<lucide-alert-triangle class="mx-auto mb-4 h-6 w-6 text-red-600" />
			<ErrorMessage message="You aren't permitted to view the this page" />
		</div>
	</div>
</template>
<script>
import { Badge } from 'frappe-ui';
import LeadDetailsDialog from './LeadDetailsDialog.vue';
import UpdateWonDialog from './UpdateWonDialog.vue';
import { h } from 'vue';
import DropdownItem from '../billing/DropdownItem.vue';
import UpdateEngagementStageDialog from './UpdateEngagementStageDialog.vue';
import UpdateLostDialog from './UpdateLostDialog.vue';
import { toast } from 'vue-sonner';
import { t } from '../../utils/language'
export default {
	name: 'PartnerLeadOverview',
	components: {
		Badge,
		LeadDetailsDialog,
		UpdateWonDialog,
		DropdownItem,
		UpdateEngagementStageDialog,
		UpdateLostDialog,
	},
	data() {
		return {
			showLeadDetailsDialog: false,
			showDialog: false,
			showUpdateEngagementStageDialog: false,
			showUpdateWonDialog: false,
			showUpdateLostDialog: false,
			errorMessage: null,
			status: null,
		};
	},
	emits: ['success'],
	resources: {
		lead() {
			return {
				type: 'document',
				doctype: 'Partner Lead',
				name: this.$route.params.leadId,
			};
		},
		updateStatus() {
			return {
				url: 'press.api.partner.update_lead_status',
				makeParams: (params) => {
					return {
						lead_name: this.lead.name,
						status: params.status,
					};
				},
				onSuccess: () => {
					this.$resources.lead.reload();
				},
				onError: (e) => {
					this.errorMessage = e.messages[0] || 'Failed to update status';
					toast.error(this.errorMessage);
				},
			};
		},
	},
	computed: {
		company_info() {
			return [
				{ label: t('Company Name'), value: this.lead?.organization_name },
				{ label: t('Lead Source'), value: this.lead?.lead_source },
				{ label: t('Lead Type'), value: this.lead?.lead_type },
				{ label: t('Industry'), value: this.lead?.domain },
				{
					label: t('Conversion Date'),
					value: this.lead?.conversion_date,
					condition: this.lead?.status === 'Won',
				},
				{
					label: t('Lost Reason'),
					value: this.lead?.lost_reason,
					condition: this.lead?.status === 'Lost',
				},
				{
					label: t('Other Reason'),
					value: this.lead?.lost_reason_specify,
					condition:
						this.lead?.status === 'Lost' && this.lead?.lost_reason === 'Other',
				},
				{
					label: t('Partner'),
					value: this.lead?.company_name,
					condition: this.$team.doc.is_desk_user,
				},
				{
					label: t('Lead Owner'),
					value: this.lead?.lead_owner,
				},
				{
					label: t('Plan Type'),
					value: this.lead?.is_starter_pack,
					condition: this.lead?.is_starter_pack !== undefined,
				},
			].filter((d) => d.condition ?? true);
		},
		contact_info() {
			return [
				{
					label: t('Full Name'),
					value: this.lead?.full_name || this.lead?.lead_name,
				},
				{ label: t('Email'), value: this.lead?.email },
				{ label: t('Country'), value: this.lead?.country },
				{ label: t('State'), value: this.lead?.state },
				{ label: t('Territory'), value: this.lead?.territory },
				{ label: t('Contact'), value: this.lead?.contact_no },
			];
		},
		deal_info() {
			return [
				{
					label: t('Plan Proposed'),
					value: this.lead?.plan_proposed,
					condition: ['Won', 'In Process'].includes(this.lead?.status),
				},
				{ label: t('Probability'), value: this.lead?.probability },
				{
					label: t('Expected Close Date'),
					value: this.lead?.estimated_closure_date,
					condition: this.lead?.status === 'In Process',
				},
				{
					label: t('Hosting'),
					value: this.lead?.hosting,
					condition: this.lead?.status === 'Won',
				},
				{
					label: t('Site URL'),
					value: this.lead?.site_url,
					condition: this.lead?.status === 'Won',
				},
			].filter((d) => d.condition ?? true);
		},
		lead() {
			return this.$resources.lead.doc;
		},
		statusOptions() {
			return [
				{
					label: t('Open'),
					value: 'Open',
					component: () =>
						h(DropdownItem, {
							label: t('Open'),
							onClick: () => {
								this._updateStatus('Open');
							},
						}),
				},
				{
					label: t('Qualification'),
					value: 'Qualification',
					component: () =>
						h(DropdownItem, {
							label: t('Qualification'),
							onClick: () => {
								this._updateStatus('Qualification');
							},
						}),
				},
				{
					label: t('Demo/Making'),
					value: 'Demo/Making',
					component: () =>
						h(DropdownItem, {
							label: t('Demo/Making'),
							onClick: () => {
								this._updateStatus('Demo/Making');
							},
						}),
				},
				{
					label: t('Follow Up'),
					value: 'Follow Up',
					component: () =>
						h(DropdownItem, {
							label: t('Follow Up'),
							onClick: () => {
								this._updateStatus('Follow Up');
							},
						}),
				},
				{
					label: t('Proposal/Quotation'),
					value: 'Proposal/Quotation',
					component: () =>
						h(DropdownItem, {
							label: t('Proposal/Quotation'),
							onClick: () => {
								this._updateStatus('Proposal/Quotation');
							},
						}),
				},
				{
					label: t('Negotiation'),
					value: 'Negotiation',
					component: () =>
						h(DropdownItem, {
							label: t('Negotiation'),
							onClick: () => {
								this._updateStatus('Negotiation');
							},
						}),
				},
				{
					label: t('Ready to Close'),
					value: 'Ready to Close',
					component: () =>
						h(DropdownItem, {
							label: t('Ready to Close'),
							onClick: () => {
								this._updateStatus('Ready to Close');
							},
						}),
				},
				{
					label: t('Won'),
					value: 'Won',
					component: () =>
						h(DropdownItem, {
							label: t('Won'),
							onClick: () => {
								this._updateStatus('Won');
							},
						}),
				},
				{
					label: t('Lost'),
					value: 'Lost',
					component: () =>
						h(DropdownItem, {
							label: t('Lost'),
							onClick: () => {
								this._updateStatus('Lost');
							},
						}),
				},
				{
					label: t('Junk'),
					value: 'Junk',
					component: () =>
						h(DropdownItem, {
							label: t('Junk'),
							onClick: () => {
								this._updateStatus('Junk');
							},
						}),
				},
				{
					label: t('Closed'),
					value: 'Closed',
					component: () =>
						h(DropdownItem, {
							label: t('Closed'),
							onClick: () => {
								this._updateStatus('Closed');
							},
						}),
				},
			];
		},
		themeMap() {
			return {
				Open: 'blue',
				Qualification: 'blue',
				'Demo/Making': 'orange',
				'Follow Up': 'blue',
				'Proposal/Quotation': 'orange',
				Negotiation: 'orange',
				'Ready to Close': 'blue',
				Won: 'green',
				Lost: 'red',
				Junk: 'gray',
				Closed: 'gray',
			};
		},
		probabilityTheme() {
			return {
				Hot: 'red',
				Warm: 'orange',
				Cold: 'blue',
			};
		},
	},
	methods: {
		_updateStatus(status) {
			if (status === this.lead.status && status !== 'In Process') return;
			if (['Ready to Close', 'Proposal/Quotation'].includes(status)) {
				this.status = status;
				this.showUpdateEngagementStageDialog = true;
			} else if (status === 'Won') {
				this.showUpdateWonDialog = true;
			} else if (status === 'Lost') {
				this.showUpdateLostDialog = true;
			} else {
				this.$resources.updateStatus.submit({ status: status });
			}
		},
	},
};
</script>
