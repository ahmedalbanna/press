<template>
	<ObjectList class="p-5" ref="objectList" :options="autoScaleRecords" />
</template>

<script>
import { h, defineAsyncComponent } from 'vue';
import { renderDialog } from '../../utils/components';
import { date } from '../../utils/format';
import { icon } from '../../utils/components';
import ObjectList from '../ObjectList.vue';

import Badge from '../global/Badge.vue';
import { t } from '../../utils/language';

export default {
	name: 'AutoScale',
	props: {
		name: String,
	},
	components: { ObjectList },
	computed: {
		autoScaleRecords() {
			return {
				doctype: 'Auto Scale Record',
				filters: {
					primary_server: this.name,
					status: ['in', 'Scheduled'],
				},
				filterControls: () => [
					{
						type: 'select',
						label: t('Action'),
						fieldname: 'action',
						options: ['', 'Scale Down', 'Scale Up'],
					},
					{
						type: 'text',
						label: t('Triggered By'),
						fieldname: 'owner',
					},
				],
				orderBy: 'creation desc',
				fields: ['owner'],
				columns: [
					{ label: t('Secondary Server'), fieldname: 'secondary_server' },

					{
						label: t('Status'),
						fieldname: 'status',
						type: 'Badge',
						align: 'center',
					},
					{
						label: t('Action'),
						fieldname: 'action',
						type: 'Component',
						align: 'center',
						component: ({ row }) =>
							h(Badge, {
								label: row.action,
								theme: row.action === 'Scale Down' ? 'orange' : 'green',
							}),
					},
					{
						label: t('Scheduled Time'),
						fieldname: 'scheduled_time',
						width: 1,
						format(row, value) {
							if (value.status !== 'Scheduled') {
								return '-';
							}
							return date(row, 'LLL');
						},
					},
					{
						label: t('Created By'),
						fieldname: 'owner',
						align: 'center',
					},
					{
						label: t('Created At'),
						fieldname: 'creation',
						type: 'Timestamp',
						align: 'right',
					},
				],

				primaryAction: () => ({
					label: t('Schedule Auto Scale'),
					slots: { prefix: icon('clock') },
					onClick: () =>
						renderDialog(
							h(
								defineAsyncComponent(
									() => import('../server/AutoscaleScheduleDialog.vue'),
								),
								{
									server: this.name,
									reloadListView: this.$refs.objectList.reloadListView,
								},
							),
						),
				}),
			};
		},
	},
};
</script>
