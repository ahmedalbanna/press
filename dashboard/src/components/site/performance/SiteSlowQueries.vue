<template>
	<div>
		<PerformanceReport
			:title="t('Slow Queries')"
			:site="name"
			:reportOptions="slowQueriesOptions"
		/>
		<SiteSlowQueryDialog
			v-if="show"
			v-model="show"
			:query="selectedQuery"
			:duration="selectedQueryDuration"
		/>
	</div>
</template>

<script>
import AlertBanner from '../../AlertBanner.vue';
import PerformanceReport from './PerformanceReport.vue';
import SiteSlowQueryDialog from './SiteSlowQueryDialog.vue';
import { t } from '../../../utils/language';

export default {
	props: ['name', 'siteVersion'],
	components: {
		PerformanceReport,
		AlertBanner,
		SiteSlowQueryDialog,
	},
	data() {
		return {
			show: false,
			selectedQuery: '',
			selectedQueryDuration: 0,
		};
	},
	computed: {
		slowQueriesOptions() {
			return {
				experimental: true,
				documentation: 'https://docs.frappe.io/cloud/performance-tuning',
				data: () => this.$resources.slowQueries.data.data,
				onRowClick: (row) => {
					this.selectedQuery = row.query;
					this.selectedQueryDuration = row.duration;
					this.show = true;
				},
				emptyStateMessage: 'No slow queries found',
				columns: [
					{
						label: t('Query'),
						fieldname: 'query',
						class: 'font-mono',
						width: '600px',
					},
					{
						label: t('Duration'),
						fieldname: 'duration',
						class: 'text-ink-gray-6',
						width: 0.3,
						align: 'right',
						format: (value) => value.toFixed(2),
					},
					{
						label: t('Rows Examined'),
						fieldname: 'rows_examined',
						class: 'text-ink-gray-6',
						align: 'right',
						width: 0.3,
					},
					{
						label: t('Rows Sent'),
						fieldname: 'rows_sent',
						class: 'text-ink-gray-6',
						align: 'right',
						width: 0.3,
					},
					{
						label: t('Count'),
						fieldname: 'count',
						class: 'text-ink-gray-6',
						align: 'right',
						width: 0.3,
					},
				],
				actions: () => [
					{
						label: t('Refresh'),
						icon: 'refresh-ccw',
						loading: this.$resources.slowQueries.loading,
						onClick: () => this.$resources.slowQueries.reload(),
					},
				],
			};
		},
	},
	methods: {
		getDateTimeRange() {
			const formatDateTime = (date) => {
				return this.$dayjs(date).format('YYYY-MM-DD HH:mm:ss');
			};

			const now = new Date();
			const startDateTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
			const endDateTime = formatDateTime(now);
			const startDateTimeFormatted = formatDateTime(startDateTime);

			return {
				startDateTime: startDateTimeFormatted,
				endDateTime: endDateTime,
			};
		},
	},
	resources: {
		slowQueries() {
			const { startDateTime, endDateTime } = this.getDateTimeRange();
			return {
				url: 'press.api.analytics.mariadb_slow_queries',
				params: {
					site: this.name,
					start_datetime: startDateTime,
					stop_datetime: endDateTime,
					max_lines: 10,
					search_pattern: '.*',
					normalize_queries: true,
					analyze: false,
				},
				auto: true,
				initialData: { columns: [], data: [] },
			};
		},
	},
};
</script>
