<template>
	<ObjectList class="p-3" :options="logsOptions" />
</template>

<script>
import { h } from 'vue';
import LucideSparkleIcon from '~icons/lucide/sparkle';
import { date } from '../../utils/format';
import ObjectList from '../ObjectList.vue';
import { t } from '../../utils/language'

export default {
	name: 'SiteLogs',
	props: {
		name: {
			type: String,
			required: true,
		},
		type: {
			type: String,
			required: false,
		},
	},
	components: {
		ObjectList,
	},
	resources: {
		logs() {
			return {
				url: 'press.api.site.logs',
				params: {
					name: this.name,
				},
				auto: true,
				initialData: [],
				cache: ['ObjectList', 'press.api.site.logs', this.name],
			};
		},
	},
	computed: {
		logs() {
			const knownTypes = [
				'frappe',
				'scheduler',
				'database',
				'pdf',
				'wkhtmltopdf',
				'ipython',
			];

			if (this.type && !knownTypes.includes(this.type)) {
				return this.$resources.logs.data.filter(
					(d) => !knownTypes.includes(d.name.split('.')[0]),
				);
			}

			// logs of a particular type
			return this.$resources.logs.data.filter(
				(d) => d.name.split('.')[0] === this.type,
			);
		},
		logsOptions() {
			if (this.type) {
				return {
					data: () => this.logs,
					route(row) {
						return {
							name: 'Site Log',
							params: { logName: row.name },
						};
					},
					columns: [
						{
							label: t('Name'),
							fieldname: 'name',
						},
						{
							label: t('Size'),
							fieldname: 'size',
							class: 'text-ink-gray-6',
							format(value) {
								return `${value} kB`;
							},
						},
						{
							label: t('Modified On'),
							fieldname: 'modified',
							format(value) {
								return value ? date(value, 'lll') : '';
							},
						},
					],
					actions: () => [
						{
							slots: {
								prefix: () => h(LucideSparkleIcon, { class: 'size-4' }),
							},
							label: t('View in Log Browser'),
							onClick: () => {
								this.$router.push({
									name: 'Log Browser',
									params: { mode: 'site', docName: this.name },
								});
							},
						},
						{
							label: t('Refresh'),
							icon: 'refresh-ccw',
							loading: this.$resources.logs.loading,
							onClick: () => this.$resources.logs.reload(),
						},
					],
				};
			} else {
				return {
					route: (row) => row.route,
					data: () => [
						{
							title: t('Scheduler Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'scheduler',
								},
							},
						},
						{
							title: t('Database Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'database',
								},
							},
						},
						{
							title: t('Frappe Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'frappe',
								},
							},
						},
						{
							title: t('PDF Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'pdf',
								},
							},
						},
						{
							title: t('IPython Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'ipython',
								},
							},
						},
						{
							title: t('Wkhtmltopdf Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'wkhtmltopdf',
								},
							},
						},
						{
							title: t('Other Logs'),
							route: {
								name: 'Site Logs',
								params: {
									name: this.name,
									type: 'other',
								},
							},
						},
					],
					columns: [
						{
							label: t('Title'),
							fieldname: 'title',
							width: 0.3,
						},
					],
					actions: () => [
						{
							slots: {
								prefix: () => h(LucideSparkleIcon, { class: 'size-4' }),
							},
							label: t('View in Log Browser'),
							onClick: () => {
								this.$router.push({
									name: 'Log Browser',
									params: { mode: 'site', docName: this.name },
								});
							},
						},
					],
				};
			}
		},
	},
};
</script>
