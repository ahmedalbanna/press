<template>
	<div>
		<PerformanceReport
			:title="t('Process List')"
			:site="name"
			:reportOptions="processListOptions"
		/>
		<SiteDatabaseProcess
			v-if="show"
			v-model="show"
			:id="selectedRow?.id ?? ''"
			:query="selectedRow?.query ?? ''"
			:host="selectedRow?.db_user_host ?? ''"
			:user="selectedRow?.db_user ?? ''"
			:state="selectedRow?.state ?? ''"
			:command="selectedRow?.command ?? ''"
			:site="name"
			@process-killed="processKilledCallback"
		/>
	</div>
</template>
<script>
import { toast } from 'vue-sonner';
import PerformanceReport from './PerformanceReport.vue';
import SiteDatabaseProcess from './SiteDatabaseProcess.vue';
import { t } from '../../../utils/language';

export default {
	name: 'SiteMariaDBProcessList',
	props: ['name'],
	components: {
		PerformanceReport,
		SiteDatabaseProcess,
	},
	data() {
		return {
			show: false,
			selectedRow: null,
		};
	},
	resources: {
		processList() {
			if (!this.name) return;
			return {
				url: 'press.api.analytics.mariadb_processlist',
				params: {
					site: this.name,
				},
				auto: true,
				initialData: [],
			};
		},
	},
	computed: {
		processListOptions() {
			return {
				data: () => this.$resources.processList.data,
				columns: [
					{
						label: t('ID'),
						fieldname: 'id',
						width: '4rem',
					},
					{
						label: t('Time'),
						fieldname: 'time',
						width: '6rem',
						align: 'right',
					},
					{
						label: t('Command'),
						fieldname: 'command',
						width: '6rem',
					},
					{
						label: t('State'),
						fieldname: 'state',
						width: '8rem',
					},
					{
						label: t('Query'),
						fieldname: 'query',
						class: 'font-mono',
					},
				],
				onRowClick: (row) => {
					this.selectedRow = row;
					this.show = true;
				},
				secondaryAction: () => {
					return {
						label: t('Refresh'),
						icon: 'refresh-ccw',
						loading: this.$resources.processList.loading,
						onClick: () => this.$resources.processList.reload(),
					};
				},
			};
		},
	},
	methods: {
		processKilledCallback() {
			toast.success('Database Process Killed');
			this.show = false;
			this.$resources.processList.reload();
		},
	},
};
</script>
