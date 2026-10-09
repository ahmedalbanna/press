<template>
	<PerformanceReport
		:title="t('Request Log Report')"
		:site="name"
		:reportOptions="requestLogsOptions"
	/>
</template>

<script>
import dayjs from '../../../utils/dayjs';
import PerformanceReport from './PerformanceReport.vue';
import { t } from '../../../utils/language';

export default {
	name: 'SiteRequestLogs',
	props: ['name'],
	components: {
		PerformanceReport,
	},
	data() {
		return {
			date: null,
			start: 0,
		};
	},
	computed: {
		requestLogsOptions() {
			return {
				resource: () => {
					return {
						url: 'press.api.analytics.request_logs',
						makeParams: (params) => {
							// for filterControls to work
							if (params) return params;

							return {
								site: this.name,
								timezone: dayjs.tz.guess(),
								sort: 'CPU Time (Descending)',
								date: this.today,
								start: this.start,
							};
						},
						auto: true,
						initialData: [],
						transform: (data) => {
							return data.map((log) => {
								log.time = dayjs(log.timestamp).format('HH:mm:ss z');
								log.method = log.request.method;
								log.path = log.request.path;
								log.status = log.request.status_code;
								log.cpu_time = log.duration / 1000000;
								return log;
							});
						},
					};
				},
				columns: [
					{ label: t('Time'), fieldname: 'time', width: 1 },
					{ label: t('Method'), fieldname: 'method', width: 0.5 },
					{ label: t('Path'), fieldname: 'path', width: 2, class: 'font-mono' },
					{
						label: t('Status Code'),
						fieldname: 'status',
						width: 0.5,
						align: 'right',
					},
					{
						label: t('CPU Time (seconds)'),
						fieldname: 'cpu_time',
						width: 1,
						class: 'text-ink-gray-6',
						align: 'right',
						format: (value) => value.toFixed(2),
					},
				],
				filterControls: () => [
					{
						type: 'select',
						label: t('Sort'),
						fieldname: 'sort',
						class: !this.$isMobile ? 'w-48' : '',
						options: [
							'Time (Ascending)',
							'Time (Descending)',
							'CPU Time (Descending)',
						],
						default: 'CPU Time (Descending)',
					},
					{
						type: 'date',
						label: t('Date'),
						fieldname: 'date',
						class: !this.$isMobile ? 'w-48' : '',
						default: this.today,
					},
				],
			};
		},
		today() {
			return dayjs().format('YYYY-MM-DD');
		},
	},
};
</script>
