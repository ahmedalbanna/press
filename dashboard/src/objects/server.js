import { defineAsyncComponent, h } from 'vue';
import { toast } from 'vue-sonner';
import LucideAppWindow from '~icons/lucide/app-window';
import ServerActions from '../components/server/ServerActions.vue';
import { getTeam } from '../data/team';
import router from '../router';
import { confirmDialog, icon, renderDialog } from '../utils/components';
import { isMobile } from '../utils/device';
import { date, duration, planTitle, userCurrency } from '../utils/format';
import { getQueryParam, setQueryParam } from '../utils/index';
import { trialDays } from '../utils/site';
import { t } from '../utils/language';
import { getJobsTab } from './common/jobs';
import { tagTab } from './common/tags';

export default {
	doctype: 'Server',
	list: {
		title: 'Servers',
		route: '/servers',
		component: () => import('../pages/servers/list/Page.vue'),
	},
	whitelistedMethods: {
		increaseDiskSize: 'increase_disk_size_for_server',
		configureAutoAddStorage: 'configure_auto_add_storage',
		changePlan: 'change_plan',
		toggleAutoIncreaseStorage: 'toggle_auto_increase_storage',
		reboot: 'reboot',
		getSSHCommand: 'get_ssh_command',
		rename: 'rename',
		cleanup: 'cleanup_unused_files',
		dropServer: 'drop_server',
		addTag: 'add_resource_tag',
		removeTag: 'remove_resource_tag',
		deleteSnapshot: 'delete_snapshot',
		lockSnapshot: 'lock_snapshot',
		unlockSnapshot: 'unlock_snapshot',
		setupSecondaryServer: 'setup_secondary_server',
		teardownSecondaryServer: 'teardown_secondary_server',
		scaleUp: 'scale_up',
		scaleDown: 'scale_down',
		addAutomatedScalingTriggers: 'add_automated_scaling_triggers',
		removeAutomatedScalingTriggers: 'remove_automated_scaling_triggers',
	},
	detail: {
		titleField: 'name',
		route: '/servers/:name',
		statusBadge({ documentResource: server }) {
			return {
				label: server.doc.status,
			};
		},
		breadcrumbs({ documentResource: server }) {
			return [
				{
					label: t('Servers'),
					route: '/servers',
				},
				{
					label: server.doc.title || server.doc.name,
					route: `/servers/${server.doc.name}`,
				},
			];
		},
		actions({ documentResource: server }) {
			let $team = getTeam();

			if (server?.doc?.status === 'Archived') {
				return [];
			}

			return [
				{
					label: t('Impersonate Server Owner'),
					title: t('Impersonate Server Owner'), // for label to pop-up on hover
					slots: {
						icon: defineAsyncComponent(
							() => import('~icons/lucide/venetian-mask'),
						),
					},
					condition: () =>
						$team.doc?.is_desk_user && server.doc.team !== $team.name,
					onClick() {
						switchToTeam(server.doc.team);
					},
				},
				{
					label: t('Options'),
					button: {
						label: t('Options'),
						slots: {
							icon: icon('more-horizontal'),
						},
					},
					options: [
						{
							label: t('View in Desk'),
							icon: icon('external-link'),
							condition: () => $team.doc?.is_desk_user,
							onClick() {
								window.open(
									`${window.location.protocol}//${
										window.location.host
									}/app/${server.doctype.replace(' ', '-').toLowerCase()}/${
										server.doc.name
									}`,
									'_blank',
								);
							},
						},
						{
							label: t('View DB in Desk'),
							icon: icon('external-link'),
							condition: () => $team.doc?.is_desk_user,
							onClick() {
								window.open(
									`${window.location.protocol}//${
										window.location.host
									}/app/database-server/${server.doc.database_server}`,
									'_blank',
								);
							},
						},
						{
							label: t('View Replication DB in Desk'),
							icon: icon('external-link'),
							condition: () =>
								$team.doc?.is_desk_user && server.doc.replication_server,
							onClick() {
								window.open(
									`${window.location.protocol}//${
										window.location.host
									}/app/database-server/${server.doc.replication_server}`,
									'_blank',
								);
							},
						},
						{
							label: t('Copy SSH Command'),
							icon: icon('clipboard'),
							condition: () => $team.doc?.is_desk_user,
							async onClick() {
								const command = await server.getSSHCommand.submit();
								await navigator.clipboard.writeText(command);
								toast.success('SSH command copied to clipboard');
							},
						},
						{
							label: t('Visit Server'),
							icon: icon('external-link'),
							condition: () =>
								server.doc.status === 'Active' && $team.doc?.is_desk_user,
							onClick() {
								window.open(`https://${server.doc.name}`, '_blank');
							},
						},
					],
				},
			];
		},
		tabs: [
			{
				label: t('Overview'),
				icon: icon('home'),
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				route: 'overview',
				type: 'Component',
				component: defineAsyncComponent(
					() => import('../components/server/ServerOverview.vue'),
				),
				props: (server) => {
					return { server: server.doc.name };
				},
			},
			{
				label: t('Analytics'),
				icon: icon('bar-chart-2'),
				condition: (server) => server.doc?.status !== 'Archived',
				route: 'analytics',
				type: 'Component',
				component: defineAsyncComponent(
					() => import('../components/server/ServerCharts.vue'),
				),
				props: (server) => {
					return {
						serverName: server.doc.name,
					};
				},
			},
			{
				label: t('Bench Analytics'),
				icon: icon('bar-chart-2'),
				condition: (server) => server.doc?.status !== 'Archived',
				route: 'bench-group-analytics',
				type: 'Component',
				component: defineAsyncComponent(
					() => import('../components/server/ReleaseGroupCharts.vue'),
				),
				props: (server) => {
					return { serverName: server.doc.name };
				},
			},
			{
				label: t('Sites'),
				icon: icon(LucideAppWindow),
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				route: 'sites',
				type: 'list',
				list: {
					doctype: 'Site',
					filters: (server) => {
						return { server: server.doc.name };
					},
					fields: [
						'plan.plan_title as plan_title',
						'plan.price_usd as price_usd',
						'plan.price_inr as price_inr',
						'group.title as group_title',
						'group.public as group_public',
						'group.team as group_team',
						'group.version as version',
						'trial_end_date',
					],
					orderBy: 'creation desc',
					searchField: 'host_name',
					route(row) {
						return { name: 'Site Detail', params: { name: row.name } };
					},
					filterControls() {
						return [
							{
								type: 'select',
								label: t('Status'),
								fieldname: 'status',
								options: [
									'',
									'Active',
									'Inactive',
									'Suspended',
									'Broken',
									'Archived',
								],
							},
							{
								type: 'select',
								label: t('Plan'),
								fieldname: 'plan.support_included',
								options: [
									{ label: t('All'), value: null },
									{ label: t('Supported'), value: '1' },
									{ label: t('Not Supported'), value: '0' },
								],
							},
							{
								type: 'link',
								label: t('Version'),
								fieldname: 'group.version',
								options: {
									doctype: 'Frappe Version',
								},
							},
							{
								type: 'link',
								label: t('Benches'),
								fieldname: 'group',
								options: {
									doctype: 'Release Group',
								},
							},
							{
								type: 'link',
								label: t('Tag'),
								fieldname: 'tags.tag',
								options: {
									doctype: 'Press Tag',
									filters: {
										doctype_name: 'Site',
									},
								},
							},
						];
					},
					columns: [
						{
							label: t('Site'),
							fieldname: 'host_name',
							width: 1.5,
							class: 'font-medium',
							format(value, row) {
								return value || row.name;
							},
						},
						{ label: t('Status'), fieldname: 'status', type: 'Badge', width: 0.6 },
						{
							label: t('Plan'),
							fieldname: 'plan',
							width: 0.85,
							format(value, row) {
								if (row.trial_end_date) {
									return trialDays(row.trial_end_date);
								}
								let $team = getTeam();
								if (row.price_usd > 0) {
									let india = $team.doc.country == 'India';
									let formattedValue = userCurrency(
										india ? row.price_inr : row.price_usd,
										0,
									);
									return `${formattedValue}/mo`;
								}
								return row.plan_title;
							},
						},
						{
							label: t('Bench'),
							fieldname: 'group_title',
							width: '15rem',
						},
						{
							label: t('Version'),
							fieldname: 'version',
							width: 0.5,
						},
					],
					primaryAction({ documentResource: server }) {
						if (server?.doc?.status !== 'Active') return {};
						return {
							label: t('New Site'),
							slots: {
								prefix: icon('plus'),
							},
							onClick() {
								router.push({
									name: 'Server New Site',
									params: { server: server.doc.name },
								});
							},
						};
					},
				},
			},
			{
				label: t('Benches'),
				icon: icon('package'),
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				route: 'groups',
				type: 'list',
				list: {
					doctype: 'Release Group',
					filters: (server) => {
						return { server: server.doc.name };
					},
					fields: [{ apps: ['app'] }, { servers: ['server'] }],
					columns: [
						{ label: t('Title'), fieldname: 'title' },
						{
							label: t('Status'),
							fieldname: 'active_benches',
							type: 'Badge',
							width: 0.5,
							format: (value, row) => {
								if (!value) return t('Awaiting Deploy');
								else return t('Active');
							},
						},
						{
							label: t('Version'),
							fieldname: 'version',
							width: 0.5,
						},
						{
							label: t('Apps'),
							fieldname: 'app',
							format: (value, row) => {
								return (row.apps || []).map((d) => d.app).join(', ');
							},
							width: '25rem',
						},
						{
							label: t('Sites'),
							fieldname: 'site_count',
							width: 0.25,
						},
					],
					filterControls() {
						return [
							{
								type: 'link',
								label: t('Version'),
								fieldname: 'version',
								options: {
									doctype: 'Frappe Version',
								},
							},
							{
								type: 'link',
								label: t('Tag'),
								fieldname: 'tags.tag',
								options: {
									doctype: 'Press Tag',
									filters: {
										doctype_name: 'Release Group',
									},
								},
							},
						];
					},
					route(row) {
						return {
							name: 'Release Group Detail',
							params: { name: row.name },
						};
					},
					primaryAction({ listResource: benches, documentResource: server }) {
						if (server?.doc?.status !== 'Active') return {};
						return {
							label: t('New Bench'),
							slots: {
								prefix: icon('plus'),
							},
							onClick() {
								router.push({
									name: 'Server New Release Group',
									params: { server: server.doc.name },
								});
							},
						};
					},
				},
			},
			{
				label: t('Snapshots'),
				icon: icon('camera'),
				condition: (server) => {
					if (!server?.doc) return true;
					return server?.doc?.provider === 'AWS EC2';
				},
				route: 'snapshots',
				type: 'list',
				list: {
					doctype: 'Server Snapshot',
					filters: (server) => {
						let filters = {
							app_server: server.doc?.name,
						};
						const snapshot_name = getQueryParam('name');
						if (snapshot_name) {
							filters.name = snapshot_name;
						}
						return filters;
					},
					filterControls() {
						const snapshot_name = getQueryParam('name');
						let filters = snapshot_name
							? [
									{
										type: 'text',
										label: t('Snapshot Name'),
										fieldname: 'name',
									},
								]
							: [
									{
										type: 'select',
										label: t('Status'),
										fieldname: 'status',
										options: [
											'',
											'Pending',
											'Processing',
											'Failure',
											'Completed',
											'Unavailable',
										],
									},
								];
						filters = filters.concat([
							{
								type: 'checkbox',
								label: t('Consistent'),
								fieldname: 'consistent',
							},
						]);
						return filters;
					},
					searchField: getQueryParam('name') ? null : 'name',
					updateFilters({ name }) {
						setQueryParam('name', name);
					},
					autoReloadAfterUpdateFilterCallback: true,
					orderBy: 'creation desc',
					fields: [
						'name',
						'status',
						'creation',
						'consistent',
						'free',
						'expire_at',
						'total_size_gb',
					],
					columns: [
						{
							label: t('Snapshot'),
							fieldname: 'name',
							width: 0.5,
							class: 'font-medium',
						},
						{
							label: t('Status'),
							fieldname: 'status',
							type: 'Badge',
							width: 0.5,
							align: 'center',
						},
						{
							label: t('Size'),
							fieldname: 'total_size_gb',
							width: 0.5,
							align: 'center',
							format(value) {
								if (!value) return '-';
								return `${value} GB`;
							},
						},
						{
							label: t('Consistent'),
							fieldname: 'consistent',
							width: 0.3,
							type: 'Icon',
							align: 'center',
							Icon(value) {
								return value ? 'check' : 'x';
							},
						},
						{
							label: t('Free'),
							fieldname: 'free',
							width: 0.3,
							type: 'Icon',
							Icon(value) {
								return value ? 'check' : 'x';
							},
						},
						{
							label: t('Locked'),
							fieldname: 'locked',
							width: 0.3,
							type: 'Icon',
							align: 'center',
							Icon(value) {
								return value ? 'lock' : 'unlock';
							},
						},
						{
							label: t('Expire At'),
							fieldname: 'expire_at',
							width: 1,
							align: 'center',
							format(value) {
								if (!value) return t('No Expiry');
								return date(value, 'llll');
							},
						},
						{
							label: t('Created At'),
							fieldname: 'creation',
							width: 1,
							align: 'right',
							format(value) {
								return date(value, 'llll');
							},
						},
					],
					primaryAction({ documentResource: server, listResource: snapshots }) {
						if (server?.doc?.status === 'Archived') return;
						return {
							label: t('New Snapshot'),
							slots: {
								prefix: icon('camera'),
							},
							onClick() {
								renderDialog(
									h(
										defineAsyncComponent(
											() =>
												import('../components/server/ServerNewSnapshotDialog.vue'),
										),
										{
											server: server.name,
											onSnapshotCreated: () => {
												snapshots.reload();
											},
										},
									),
								);
							},
						};
					},
					rowActions({ row, documentResource: server }) {
						return [
							{
								label: t('View Details'),
								onClick() {
									let ServerSnapshotDetailsDialog = defineAsyncComponent(
										() =>
											import('../components/server/ServerSnapshotDetailsDialog.vue'),
									);
									renderDialog(
										h(ServerSnapshotDetailsDialog, {
											name: row.name,
										}),
									);
								},
							},
							{
								label: t('Recover Sites'),
								condition: () => row.status === 'Completed',
								onClick() {
									let ServerSnapshotRecoverSitesDialog = defineAsyncComponent(
										() =>
											import('../components/server/ServerSnapshotRecoverSitesDialog.vue'),
									);
									renderDialog(
										h(ServerSnapshotRecoverSitesDialog, {
											name: row.name,
										}),
									);
								},
							},
							{
								label: t('Lock'),
								condition: () => row.status === 'Completed' && !row.locked,
								onClick() {
									confirmDialog({
										title: t('Lock Snapshot'),
										message: t(
											'Are you sure you want to lock this snapshot? This will prevent the snapshot from being deleted accidentally.',
										),
										primaryAction: {
											label: t('Lock'),
											onClick: ({ hide }) => {
												toast.promise(
													server.lockSnapshot.submit(
														{
															snapshot_name: row.name,
														},
														{
															onSuccess() {
																hide();
															},
														},
													),
													{
														loading: t('Locking snapshot...'),
														success: 'Snapshot will be locked shortly',
														error: (err) => {
															return err.messages?.length
																? err.messages.join('\n')
																: err.message || 'Failed to lock snapshot';
														},
													},
												);
											},
										},
									});
								},
							},
							{
								label: t('Unlock'),
								condition: () => row.status === 'Completed' && row.locked,
								onClick() {
									confirmDialog({
										title: t('Unlock Snapshot'),
										message: t(
											'Are you sure you want to unlock this snapshot ? After unlocking, the snapshot can be deleted by end-user.',
										),
										primaryAction: {
											label: t('Unlock'),
											onClick: ({ hide }) => {
												toast.promise(
													server.unlockSnapshot.submit(
														{
															snapshot_name: row.name,
														},
														{
															onSuccess() {
																hide();
															},
														},
													),
													{
														loading: t('Unlocking snapshot...'),
														success: 'Snapshot will be unlocked shortly',
														error: (err) => {
															return err.messages?.length
																? err.messages.join('\n')
																: err.message || 'Failed to unlock snapshot';
														},
													},
												);
											},
										},
									});
								},
							},
							{
								label: t('Delete'),
								condition: () => row.status === 'Completed',
								onClick() {
									confirmDialog({
										title: t('Delete Snapshot'),
										message: t(
											'Are you sure you want to delete this snapshot? This will delete the snapshot and all associated recovered data.',
										),
										primaryAction: {
											label: t('Delete'),
											theme: 'red',
											onClick: ({ hide }) => {
												toast.promise(
													server.deleteSnapshot.submit(
														{
															snapshot_name: row.name,
														},
														{
															onSuccess() {
																hide();
															},
														},
													),
													{
														loading: t('Deleting snapshot...'),
														success: 'Snapshot deleted successfully',
														error: (err) => {
															return err.messages?.length
																? err.messages.join('\n')
																: err.message || 'Failed to delete snapshot';
														},
													},
												);
											},
										},
									});
								},
							},
						];
					},
				},
			},
			getJobsTab('Server'),
			{
				label: t('Plays'),
				icon: icon('play'),
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				childrenRoutes: ['Server Play'],
				route: 'plays',
				type: 'list',
				searchField: 'play',
				list: {
					doctype: 'Ansible Play',
					filterControls({ documentResource: server }) {
						return [
							{
								type: 'select',
								label: t('Server'),
								fieldname: 'server',
								options: [
									server.doc.name,
									server.doc.database_server,
									server.doc.replication_server,
								].filter(Boolean),
							},
						];
					},
					filters: (server) => {
						return {
							server: [
								'in',
								[
									server.doc.name,
									server.doc.database_server,
									server.doc.replication_server,
								].filter(Boolean),
							],
						};
					},
					route(row) {
						return {
							name: 'Server Play',
							params: { id: row.name },
						};
					},
					orderBy: 'creation desc',
					fields: ['server', 'end'],
					columns: [
						{
							label: t('Play'),
							fieldname: 'play',
							width: 2,
						},
						{
							label: t('Status'),
							fieldname: 'status',
							type: 'Badge',
							width: 0.5,
						},
						{
							label: t('Server'),
							fieldname: 'server',
							width: 2,
						},
						{
							label: t('Duration'),
							fieldname: 'duration',
							width: 0.5,
							format(value, row) {
								if (row.job_id === 0 || !row.end) return;
								return duration(value);
							},
						},
						{
							label: '',
							fieldname: 'creation',
							type: 'Timestamp',
							align: 'right',
						},
					],
				},
			},
			{
				label: t('Actions'),
				icon: icon('sliders'),
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				route: 'actions',
				type: 'Component',
				component: ServerActions,
				props: (server) => {
					return { server: server.doc.name };
				},
			},
			{
				label: t('Auto Scale'),
				icon: icon('maximize-2'),
				route: 'auto-scale',
				type: 'Component',
				condition: (server) => {
					if (!server?.doc) return true;
					return server?.doc?.secondary_server;
				},
				redirectTo: 'Triggered',
				childrenRoutes: ['Triggered', 'Scheduled'],
				nestedChildrenRoutes: [
					{
						name: 'Triggered',
						path: 'triggered',
						component: () =>
							import('../components/server/AutoScaleTriggered.vue'),
					},
					{
						name: 'Scheduled',
						path: 'scheduled',
						component: () =>
							import('../components/server/AutoScaleScheduled.vue'),
					},
				],
				component: defineAsyncComponent(
					() => import('../components/server/AutoScaleTabs.vue'),
				),
				props: (server) => {
					return {
						server: server.doc.name,
					};
				},
			},
			{
				label: t('Firewall'),
				icon: icon('shield'),
				condition: (server) => {
					return (
						server.doc?.status !== 'Archived' && !server.doc?.is_self_hosted
					);
				},
				route: 'firewall',
				type: 'Component',
				component: defineAsyncComponent(
					() => import('../components/server/ServerFirewall.vue'),
				),
				props: (server) => {
					return {
						id: server.doc.name,
					};
				},
			},
			tagTab('Server'),
			{
				label: t('Activity'),
				icon: icon('activity'),
				route: 'activity',
				type: 'list',
				condition: (server) => {
					return server.doc?.status !== 'Archived';
				},
				list: {
					doctype: 'Server Activity',
					filters: (server) => {
						return {
							document_name: [
								'in',
								[server.doc?.name, server.doc?.database_server],
							],
						};
					},
					orderBy: 'creation desc',
					fields: ['owner'],
					columns: [
						{
							label: t('Action'),
							fieldname: 'action',
							format(value, row) {
								return `${row.action} by ${row.owner}`;
							},
						},
						{
							label: t('Server'),
							fieldname: 'document_name',
						},
						{
							label: t('Description'),
							fieldname: 'reason',
							class: 'text-ink-gray-6',
						},
						{
							label: '',
							fieldname: 'creation',
							type: 'Timestamp',
							align: 'right',
						},
					],
					filterControls() {
						return [
							{
								type: 'select',
								label: t('Action'),
								fieldname: 'action',
								class: !isMobile() ? 'w-52' : '',
								options: [
									'',
									'Created',
									'Reboot',
									'Volume',
									'Terminated',
									'Incident',
									'Disk Size Change',
								],
							},
						];
					},
				},
			},

			{
				label: t('Plan History'),
				icon: icon('credit-card'),
				route: 'plan-history',
				type: 'list',
				list: {
					doctype: 'Plan Change',
					filters: (server) => {
						return {
							document_name: [
								'in',
								[server.doc?.name, server.doc?.database_server].filter(Boolean),
							],
						};
					},
					fields: ['from_plan', 'to_plan', 'type', 'timestamp', 'owner', 'document_type'],
					orderBy: 'timestamp desc',
					columns: [
						{
							label: t('Server Type'),
							fieldname: 'document_type',
							format(value) {
								if (value === 'Server') return t('Application Server');
								if (value === 'Database Server') return t('Database Server');
								return value || '—';
							},
						},
						{
							label: t('Changed From'),
							fieldname: 'from_plan',
							class: 'text-gray-600',
							format(value) {
								return value || '—';
							},
						},
						{
							label: t('Changed To'),
							fieldname: 'to_plan',
						},
						{
							label: t('Type'),
							fieldname: 'type',
							type: 'Badge',
							theme(value) {
								if (value === 'Upgrade') return 'green';
								if (value === 'Downgrade') return 'red';
								return 'gray';
							},
						},
						{
							label: t('Changed By'),
							fieldname: 'owner',
							class: 'text-gray-600',
						},
						{
							label: t('Date'),
							fieldname: 'timestamp',
							type: 'Timestamp',
							align: 'right',
						},
					],
					filterControls() {
						return [
							{
								type: 'select',
								label: t('Server Type'),
								fieldname: 'document_type',
								options: [
									{ label: t('All'), value: null },
									{ label: t('Application Server'), value: 'Server' },
									{ label: t('Database Server'), value: 'Database Server' },
								],
							},
						];
					},
				},
			},
		],
	},
	routes: [
		{
			name: 'Server Job',
			path: 'jobs/:id',
			component: () => import('../pages/JobPage.vue'),
		},
		{
			name: 'Server Play',
			path: 'plays/:id',
			component: () => import('../pages/PlayPage.vue'),
		},
		{
			name: 'Auto Scale Steps',
			path: 'auto-scale-steps/:id',
			component: () => import('../components/server/AutoScaleSteps.vue'),
		},
	],
};
