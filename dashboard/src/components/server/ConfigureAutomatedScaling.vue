<template>
	<Dialog
		:options="{
			title: t('Auto Scale Triggers'),
			size: '2xl',
		}"
		v-model="show"
	>
		<template #body-content>
			<div
				v-if="$resources.configuredAutoscales.loading"
				class="flex w-full items-center justify-center gap-2 py-32 text-ink-gray-7"
			>
				<Spinner class="w-4" /> {{ t('Loading') }}
			</div>
			<div v-else>
				<AlertBanner
					type="info"
					:showIcon="false"
					class="mb-3"
					title="When both CPU and Memory thresholds are set, scaling will trigger if either condition is met.
					<br>{{ t('Please refer to the') }} <a href='https://docs.frappe.io/cloud/application-server-horizontal-scaling#application-server-horizontal-scaling'
					target='_blank' class='underline'>documentation</a> for more information."
				/>
				<div class="flex justify-end gap-2">
					<Button
						v-if="selectedTriggers.length > 0"
						variant="subtle"
						class="mb-3"
						theme="red"
						iconLeft="trash-2"
						@click="onRemoveTrigger"
					>
						{{ t('Remove') }}
					</Button>
					<Button
						variant="solid"
						class="mb-3"
						iconLeft="plus"
						@click="openAddTriggerDialog"
					>
						New
					</Button>
					<Button
						variant="subtle"
						class="mb-3"
						icon="refresh-cw"
						:loading="$resources.configuredAutoscales.loading"
						@click="$resources.configuredAutoscales.submit()"
					>
						{{ t('Refresh') }}
					</Button>
				</div>
				<GenericList
					:options="autoScaleTriggerOptions"
					@update:selections="onSelectionUpdate"
				/>
			</div>
		</template>
	</Dialog>
</template>

<script>
import { getCachedDocumentResource } from 'frappe-ui';
import { Button } from 'frappe-ui';
import { h } from 'vue';
import { toast } from 'vue-sonner';
import { confirmDialog } from '../../utils/components';
import AlertBanner from '../AlertBanner.vue';
import GenericList from '../GenericList.vue';
import Badge from '../global/Badge.vue';
import { t } from '../../utils/language';

export default {
	name: 'AutoScale',
	props: {
		name: {
			type: String,
			required: true,
		},
	},
	components: { GenericList },
	data() {
		return {
			show: true,
			selectedTriggers: [],
			triggers: [],
		};
	},

	resources: {
		configuredAutoscales() {
			return {
				url: 'press.api.server.get_configured_autoscale_triggers',
				params: { name: this.name },
				auto: true,
				initialData: [],
				onSuccess: (data) => {
					this.triggers = [...(data || [])];
				},
			};
		},
	},

	computed: {
		server() {
			return getCachedDocumentResource('Server', this.name);
		},
		autoScaleTriggerOptions() {
			return {
				data: this.triggers,
				selectable: true,
				columns: [
					{ label: t('Metric'), fieldname: 'metric', type: 'text' },
					{
						label: t('Threshold'),
						fieldname: 'threshold',
						type: 'text',
						format: (v) => `${v}%`,
					},
					{
						label: t('Action'),
						fieldname: 'action',
						type: 'Component',
						align: 'center',
						component: ({ row }) => {
							return h(Badge, {
								label: row.action,
								theme: row.action === 'Scale Down' ? 'orange' : 'green',
							});
						},
					},
				],
				emptyState: {
					title: t('No Autoscale Triggers found'),
					description: 'You have not configured any autoscale triggers yet',
				},
			};
		},
	},
	methods: {
		onSelectionUpdate(selection) {
			this.selectedTriggers = Array.from(selection || []);
		},

		onRemoveTrigger() {
			const server = this.server;
			toast.promise(
				server.removeAutomatedScalingTriggers.submit({
					triggers: this.selectedTriggers,
				}),
				{
					loading: 'Removing trigger...',
					success: () => {
						this.$resources.configuredAutoscales.submit();
						this.selectedTriggers = [];
						return 'Removed Trigger';
					},
					error: 'Failed to remove trigger',
				},
			);
		},

		openAddTriggerDialog() {
			this.show = false;
			const server = this.server;

			confirmDialog({
				title: t('Add Autoscaling Trigger'),
				message: t('Create a new autoscaling rule for this server.'),
				fields: [
					{
						label: t('Metric'),
						fieldname: 'metric',
						type: 'select',
						options: [
							{ label: t('CPU Usage'), value: 'CPU' },
							{ label: t('Memory'), value: 'Memory' },
						],
						default: 'CPU',
						required: true,
					},

					{
						label: t('Threshold (%)'),
						fieldname: 'threshold',
						type: 'float',
						required: true,
					},
					{
						label: t('Action'),
						fieldname: 'action',
						type: 'select',
						options: [
							{ label: t('Scale Up'), value: 'Scale Up' },
							{ label: t('Scale Down'), value: 'Scale Down' },
						],
						required: true,
					},
				],
				primaryAction: {
					label: t('Add Trigger'),
				},
				onSuccess: ({ hide, values }) => {
					const threshold = parseFloat(values.threshold);

					if (isNaN(threshold)) {
						toast.error('Threshold must be a valid number');
						return;
					}

					toast.promise(
						server.addAutomatedScalingTriggers.submit({
							metric: values.metric,
							threshold,
							action: values.action,
						}),
						{
							loading: 'Adding trigger...',
							success: () => {
								hide();
								return 'Trigger added';
							},
							error: 'Failed to add trigger',
						},
					);
				},
			});
		},
	},
};
</script>
