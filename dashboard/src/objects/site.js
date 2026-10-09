import { Badge, createListResource, LoadingIndicator } from 'frappe-ui'
import { defineAsyncComponent, h } from 'vue'
import { toast } from 'vue-sonner'
import ArrowLeftRightIcon from '~icons/lucide/arrow-left-right'
import AddDomainDialog from '../components/AddDomainDialog.vue'
import GenericDialog from '../components/GenericDialog.vue'
import ObjectList from '../components/ObjectList.vue'
import SiteActions from '../components/SiteActions.vue'
import { getTeam, switchToTeam } from '../data/team'
import router from '../router'
import { getRunningJobs } from '../utils/agentJob'
import { confirmDialog, icon, renderDialog } from '../utils/components'
import { isMobile } from '../utils/device'
import { date, escapeHtml } from '../utils/format'
import { getDocResource } from '../utils/resource'
import { getToastErrorMessage } from '../utils/toast'
import { t, tr } from '../utils/language'
import { getFrappeUpdateBanner, getUpsellBanner } from './common'
import { getAppsTab } from './common/apps'
import { getBackupsTab } from './site/backups'

// prefilled so only the ticket id has to be typed; on its own it is not a reason
const LOGIN_REASON_PREFIX = t('Investigating ')

// A scheduled action runs as Administrator, which means nothing to a customer.
// Site.get_archival_details does the same for the banner.
function getActorName(owner) {
	return owner === 'Administrator' ? 'AlbannaTech' : owner
}

// The banner names who and when; the Activity tab carries the reason and the rest.
function getArchivalMessage(site) {
	const details = site.archival_details
	if (!details) return t('This site is archived. It cannot be used again.')

	return tr('Archived by {by} on {date}', {
		by: escapeHtml(details.archived_by),
		date: date(details.archived_on, 'LLL'),
	})
}

function jobLink(site, job, text) {
	if (!job) return text
	return `<a href="/dashboard/sites/${site.doc.name}/insights/jobs/${job}" class="underline" target="_blank">${text}</a>`
}

function canRestoreTables(site) {
	// Only a logical backup of a migrate update makes the dump that the restore reads
	return (
		site.doc?.fatal_site_update &&
		site.doc?.status === 'Broken' &&
		site.doc?.fatal_update?.deploy_type === 'Migrate' &&
		site.doc?.fatal_update?.backup_type === 'Logical'
	)
}

function confirmRestoreTables(site) {
	confirmDialog({
		title: t('Restore Tables'),
		message: `${tr(
			'The {update} failed and the {recovery} could not restore the tables.',
			{
				update: jobLink(
					site,
					site.doc?.fatal_update?.update_job,
					t('last update'),
				),
				recovery: jobLink(
					site,
					site.doc?.fatal_update?.recover_job,
					t('automatic recovery'),
				),
			},
		)}<br><br>${t('Re-attempt the recovery manually?')}<br><br>${tr(
			'The site database goes back to <b>{date}</b>, when the last update started. <b>Any data written to the site after that time is lost.</b> You cannot undo this.',
			{ date: date(site.doc?.fatal_update?.update_start, 'lll') },
		)}`,
		primaryAction: {
			label: t('Restore Tables'),
			theme: 'red',
		},
		onSuccess({ hide }) {
			if (site.restoreTables.loading) return
			toast.promise(site.restoreTables.submit(), {
				loading: t('Starting table restore...'),
				success: () => {
					hide()
					return t('Table restore started')
				},
				error: (e) => getToastErrorMessage(e),
			})
		},
	})
}

export default {
	doctype: 'Site',
	whitelistedMethods: {
		activate: 'activate',
		addDomain: 'add_domain',
		archive: 'archive',
		backup: 'schedule_backup',
		clearSiteCache: 'clear_site_cache',
		deactivate: 'deactivate',
		disableReadWrite: 'disable_read_write',
		enableReadWrite: 'enable_read_write',
		installApp: 'install_app',
		uninstallApp: 'uninstall_app',
		migrate: 'migrate',
		moveToBench: 'move_to_bench',
		moveToGroup: 'move_to_group',
		loginAsAdmin: 'login_as_admin',
		loginAsTeam: 'login_as_team',
		isSetupWizardComplete: 'is_setup_wizard_complete',
		reinstall: 'reinstall',
		restoreTables: 'restore_tables',
		removeDomain: 'remove_domain',
		redirectToPrimary: 'set_redirect',
		removeRedirect: 'unset_redirect',
		setPrimaryDomain: 'set_host_name',
		fetchCertificate: 'fetch_certificate',
		restoreSite: 'restore_site',
		restoreSiteFromFiles: 'restore_site_from_files',
		restoreSiteFromPhysicalBackup: 'restore_site_from_physical_backup',
		scheduleUpdate: 'schedule_update',
		editScheduledUpdate: 'edit_scheduled_update',
		cancelUpdate: 'cancel_scheduled_update',
		getAutoUpdateWindow: 'get_auto_update_window',
		setPlan: 'set_plan',
		updateConfig: 'update_config',
		deleteConfig: 'delete_config',
		sendTransferRequest: 'send_change_team_request',
		addTag: 'add_resource_tag',
		removeTag: 'remove_resource_tag',
		getBackupDownloadLink: 'get_backup_download_link',
		getBackupSchedule: 'get_backup_schedule',
		updateBackupSchedule: 'update_backup_schedule',
		fetchDatabaseTableSchemas: 'fetch_database_table_schemas',
		fetchSitesDataForExport: 'fetch_sites_data_for_export',
	},
	list: {
		route: '/sites',
		title: 'Sites',
		component: () => import('../pages/sites/list/Page.vue'),
	},
	detail: {
		titleField: 'name',
		route: '/sites/:name',
		statusBadge({ documentResource: site }) {
			return { label: site.doc.status }
		},
		banner({ documentResource: site }) {
			if (canRestoreTables(site)) {
				return {
					title:
						'The last update failed and the tables could not be restored. The site stays broken until you <b>Restore Tables</b>.',
					type: 'error',
				}
			}
			if (site.doc.fatal_site_update && site.doc.status === 'Broken') {
				return {
					title: t(
						'The last update failed and the site could not be recovered. Contact support to bring it back.',
					),
					type: 'error',
				}
			}
			if (site.doc.status === 'Archived') {
				return { title: getArchivalMessage(site.doc), type: 'info' }
			}
			return getFrappeUpdateBanner(site.doc, t('This site'))
		},
		breadcrumbs({ items, documentResource: site }) {
			let breadcrumbs = []
			let $team = getTeam()
			let siteCrumb = {
				label: site.doc.host_name || site.doc?.name,
				route: `/sites/${site.doc?.name}`,
			}

			if (
				(site.doc.server_team == $team.doc?.name &&
					site.doc.group_team == $team.doc?.name) ||
				$team.doc?.is_desk_user ||
				$team.doc?.is_support_agent
			) {
				breadcrumbs.push({
					label: site.doc?.server_title || site.doc?.server,
					route: `/servers/${site.doc?.server}`,
				})
			}
			if (
				site.doc.group_team == $team.doc?.name ||
				$team.doc?.is_desk_user ||
				$team.doc?.is_support_agent
			) {
				breadcrumbs.push(
					{
						label: site.doc?.group_title,
						route: `/groups/${site.doc?.group}`,
					},
					siteCrumb,
				)
			} else {
				breadcrumbs.push(...items.slice(0, -1), siteCrumb)
			}
			return breadcrumbs
		},
		tabs: [
			{
				label: t('Overview'),
				icon: icon('home'),
				route: 'overview',
				type: 'Component',
				condition: (site) => site.doc?.status !== 'Archived',
				component: defineAsyncComponent(
					() => import('../components/SiteOverview.vue'),
				),
				props: (site) => {
					return { site: site.doc?.name }
				},
			},
			{
				label: t('Insights'),
				icon: icon('bar-chart-2'),
				route: 'insights',
				type: 'Component',
				condition: (site) => site.doc?.status !== 'Archived',
				redirectTo: 'Site Analytics',
				childrenRoutes: [
					'Site Jobs',
					'Site Job',
					'Site Logs',
					'Site Log',
					'Site Analytics',
					'Site Performance Reports',
					'Site Performance Request Logs',
					'Site Performance Slow Queries',
					'Site Performance Process List',
					'Site Performance Request Log',
					'Site Performance Deadlock Report',
				],
				nestedChildrenRoutes: [
					{
						name: 'Site Analytics',
						path: 'analytics',
						component: () => import('../components/site/SiteAnalytics.vue'),
					},
					{
						name: 'Site Jobs',
						path: 'jobs',
						component: () => import('../components/site/SiteJobs.vue'),
					},
					{
						name: 'Site Job',
						path: 'jobs/:id',
						component: () => import('../pages/JobPage.vue'),
					},
					{
						name: 'Site Logs',
						path: 'logs/:type?',
						component: () => import('../components/site/SiteLogs.vue'),
					},
					{
						name: 'Site Log',
						path: 'logs/view/:logName',
						component: () => import('../pages/LogPage.vue'),
					},
					{
						name: 'Site Performance Reports',
						path: 'performance',
						component: () =>
							import('../components/site/performance/SitePerformance.vue'),
					},
					{
						name: 'Site Performance Slow Queries',
						path: 'performance/slow-queries',
						component: () =>
							import('../components/site/performance/SiteSlowQueries.vue'),
					},
					{
						name: 'Site Performance Process List',
						path: 'performance/process-list',
						component: () =>
							import('../components/site/performance/SiteProcessList.vue'),
					},
					{
						name: 'Site Performance Request Logs',
						path: 'performance/request-log',
						component: () =>
							import('../components/site/performance/SiteRequestLogs.vue'),
					},
					{
						name: 'Site Performance Deadlock Report',
						path: 'performance/deadlock-report',
						component: () =>
							import('../components/site/performance/SiteDeadlockReport.vue'),
					},
				],
				component: defineAsyncComponent(
					() => import('../components/site/SiteInsights.vue'),
				),
				props: (site) => {
					return { site: site.doc?.name }
				},
			},
			getAppsTab(true),
			{
				label: t('Domains'),
				icon: icon('external-link'),
				route: 'domains',
				type: 'list',
				condition: (site) => {
					return site.doc?.status !== 'Archived'
				},
				list: {
					doctype: 'Site Domain',
					fields: ['redirect_to_primary'],
					filters: (site) => {
						return { site: site.doc?.name }
					},
					columns: [
						{
							label: t('Domain'),
							fieldname: 'domain',
						},
						{
							label: t('Status'),
							fieldname: 'status',
							type: 'Badge',
						},
						{
							label: t('Primary'),
							fieldname: 'primary',
							type: 'Icon',
							Icon(value) {
								return value ? 'check' : ''
							},
						},
						{
							label: t('DNS Type'),
							fieldname: 'dns_type',
							type: 'Badge',
						},
					],
					banner({ documentResource: site }) {
						if (site.doc.broken_domain_error) {
							return {
								title: t(
									'There was an error fetching an https certificate for your domain.',
								),
								type: 'error',
								button: {
									label: t('View Error'),
									variant: 'outline',
									onClick() {
										renderDialog(
											h(
												GenericDialog,
												{
													options: {
														title: t('Error fetching certificate'),
														size: 'xl',
													},
												},
												{
													default: () => {
														return h('pre', {
															class:
																'whitespace-pre-wrap text-sm rounded border-2 p-3 border-outline-gray-1 bg-surface-gray-2',
															innerHTML: site.doc.broken_domain_error,
														})
													},
												},
											),
										)
									},
								},
							}
						} else {
							return null
						}
					},
					primaryAction({ listResource: domains, documentResource: site }) {
						return {
							label: t('Add Domain'),
							slots: {
								prefix: icon('plus'),
							},
							onClick() {
								renderDialog(
									h(AddDomainDialog, {
										site: site.doc,
										onDomainAdded() {
											domains.reload()
										},
									}),
								)
							},
						}
					},
					rowActions({ row, listResource: domains, documentResource: site }) {
						return [
							{
								label: t('Remove'),
								condition: () => row.domain !== site.doc?.name,
								onClick() {
									confirmDialog({
										title: t('Remove Domain'),
										message: tr(
											'Are you sure you want to remove the domain <b>{domain}</b> from the site <b>{name}</b>?',
											{ domain: row.domain, name: site.doc?.name },
										),
										onSuccess({ hide }) {
											if (site.removeDomain.loading) return
											toast.promise(
												site.removeDomain.submit({
													domain: row.domain,
												}),
												{
													loading: t('Removing domain...'),
													success: () => {
														hide()
														return t('Domain removed')
													},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
							{
								label: t('Set Primary'),
								condition: () => !row.primary && row.status === 'Active',
								onClick() {
									confirmDialog({
										title: t('Set Primary Domain'),
										message: tr(
											'Are you sure you want to set the domain <b>{domain}</b> as the primary domain for the site <b>{name}</b>?',
											{ domain: row.domain, name: site.doc?.name },
										),
										onSuccess({ hide }) {
											if (site.setPrimaryDomain.loading) return
											toast.promise(
												site.setPrimaryDomain.submit({
													domain: row.domain,
												}),
												{
													loading: t('Setting primary domain...'),
													success: () => {
														hide()
														return t('Primary domain set')
													},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
							{
								label: t('Redirect to Primary'),
								condition: () =>
									!row.primary &&
									!row.redirect_to_primary &&
									row.status === 'Active',
								onClick() {
									confirmDialog({
										title: t('Redirect Domain'),
										message: tr(
											'Are you sure you want to redirect the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?',
											{ domain: row.domain, host: site.doc?.host_name },
										),
										onSuccess({ hide }) {
											if (site.redirectToPrimary.loading) return
											toast.promise(
												site.redirectToPrimary.submit({
													domain: row.domain,
												}),
												{
													loading: t('Redirecting domain...'),
													success: () => {
														hide()
														return t('Domain redirected')
													},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
							{
								label: t('Remove Redirect'),
								condition: () =>
									!row.primary &&
									row.redirect_to_primary &&
									row.status === 'Active',
								onClick() {
									confirmDialog({
										title: t('Remove Redirect'),
										message: tr(
											'Are you sure you want to remove the redirect from the domain <b>{domain}</b> to the primary domain of the site <b>{host}</b>?',
											{ domain: row.domain, host: site.doc?.host_name },
										),
										onSuccess({ hide }) {
											if (site.removeRedirect.loading) return
											toast.promise(
												site.removeRedirect.submit({
													domain: row.domain,
												}),
												{
													loading: t('Removing redirect...'),
													success: () => {
														hide()
														return t('Redirect removed')
													},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
							{
								label: t('Fetch Certificate'),
								condition: () =>
									row.status === 'Broken' &&
									site.doc.broken_domain_error &&
									site.doc.tls_cert_retry_count < 8,
								onClick() {
									confirmDialog({
										title: t('Fetch Certificate'),
									message: `${tr(
										'Are you sure you want to retry fetching the certificate for the domain <b>{domain}</b>?',
										{ domain: row.domain },
									)}<br><br>${t(
										'<b>Note:</b> This action is rate limited. Please allow some time for dns changes (if any) to propagate before retrying.',
									)}`,
										onSuccess({ hide }) {
											if (site.fetchCertificate.loading) return
											toast.promise(
												site.fetchCertificate.submit({
													domain: row.domain,
												}),
												{
									loading: t('Fetching certificate...'),
									success: () => {
										hide()
										return t(
											'Certificate fetch scheduled. Please wait a few minutes.',
										)
									},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
						]
					},
				},
			},
			getBackupsTab(),
			{
				label: t('Site Config'),
				icon: icon('settings'),
				route: 'site-config',
				type: 'list',
				condition: (site) => {
					return site.doc?.status !== 'Archived'
				},
				list: {
					doctype: 'Site Config',
					filters: (site) => {
						return { parent: site.doc?.name, parenttype: 'Site' }
					},
					fields: ['name'],
					pageLength: 999,
					orderBy: 'creation desc',
					columns: [
						{
							label: t('Config Name'),
							fieldname: 'key',
							width: 1,
							format(value, row) {
								if (row.title) {
									return `${row.title} (${row.key})`
								}
								return row.key
							},
						},
						{
							label: t('Config Value'),
							fieldname: 'value',
							class: 'font-mono',
							width: 2,
						},
						{
							label: t('Type'),
							fieldname: 'type',
							type: 'Badge',
							width: '100px',
						},
					],
					primaryAction({ listResource: configs, documentResource: site }) {
						return {
							label: t('Add Config'),
							slots: {
								prefix: icon('plus'),
							},
							onClick() {
								let ConfigEditorDialog = defineAsyncComponent(
									() => import('../components/ConfigEditorDialog.vue'),
								)
								renderDialog(
									h(ConfigEditorDialog, {
										site: site.doc?.name,
										onSuccess() {
											configs.reload()
										},
									}),
								)
							},
						}
					},
					secondaryAction({ listResource: configs }) {
						return {
							label: t('Preview'),
							slots: {
								prefix: icon('eye'),
							},
							onClick() {
								let ConfigPreviewDialog = defineAsyncComponent(
									() => import('../components/ConfigPreviewDialog.vue'),
								)
								renderDialog(
									h(ConfigPreviewDialog, {
										configs: configs.data,
									}),
								)
							},
						}
					},
					rowActions({ row, listResource: configs, documentResource: site }) {
						return [
							{
								label: t('Edit'),
								onClick() {
									let ConfigEditorDialog = defineAsyncComponent(
										() => import('../components/ConfigEditorDialog.vue'),
									)
									renderDialog(
										h(ConfigEditorDialog, {
											site: site.doc?.name,
											config: row,
											onSuccess() {
												configs.reload()
											},
										}),
									)
								},
							},
							{
								label: t('Delete'),
								onClick() {
									confirmDialog({
										title: t('Delete Config'),
										message: tr('Are you sure you want to delete the config <b>{key}</b>?', {
											key: row.key,
										}),
										onSuccess({ hide }) {
											if (site.deleteConfig.loading) return
											toast.promise(
												site.deleteConfig.submit(
													{ key: row.key },
													{
														onSuccess: () => {
															configs.reload()
															hide()
														},
													},
												),
												{
													loading: t('Deleting config...'),
													success: () => `Config ${row.key} removed`,
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
						]
					},
				},
			},
			{
				label: t('Migrations'),
				icon: icon(ArrowLeftRightIcon),
				route: 'migrations',
				type: 'list',
				condition: (site) => {
					return site.doc?.status !== 'Archived'
				},
				childrenRoutes: ['Site Migration'],
				list: {
					documentation:
						'https://docs.frappe.io/cloud/site/site-migrations/introduction-to-site-migration',
					doctype: 'Site Action',
					filters: (site) => {
						return { site: site.doc?.name }
					},
					orderBy: 'creation',
					fields: ['action_type', 'status', 'scheduled_time', 'owner'],
					columns: [
						{
							label: t('Migration'),
							fieldname: 'action_type',
							width: 1,
						},
						{
							label: t('Status'),
							fieldname: 'status',
							type: 'Badge',
							width: 0.6,
						},
						{
							label: t('Created By'),
							fieldname: 'owner',
						},
						{
							label: t('Scheduled At'),
							fieldname: 'scheduled_time',
							format(value) {
								return date(value, 'lll')
							},
						},
						// {
						// 	label: t('Updated On'),
						// 	fieldname: 'updated_on',
						// 	format(value) {
						// 		return date(value, 'lll');
						// 	},
						// },
					],
					route(row) {
						return {
							name: 'Site Migration',
							params: { id: row.name },
						}
					},
					primaryAction({ listResource: backups, documentResource: site }) {
						return {
							label: t('Trigger Migration'),
							slots: {
								prefix: icon('upload-cloud'),
							},
							loading: site.backup.loading,
							onClick() {
								renderDialog(
									h(
										defineAsyncComponent(
											() => import('../components/site/SiteMigration.vue'),
										),
										{
											site: site.name,
										},
									),
								)
							},
						}
					},
				},
			},
			{
				label: t('Updates'),
				icon: icon('arrow-up-circle'),
				route: 'updates',
				type: 'list',
				condition: (site) => {
					return site.doc?.status !== 'Archived'
				},
				childrenRoutes: ['Site Update'],
				list: {
					doctype: 'Site Update',
					filters: (site) => {
						return { site: site.doc?.name }
					},
					orderBy: 'creation desc',
					fields: [
						'difference',
						'update_job.end as updated_on',
						'update_job',
						'backup_type',
						'recover_job',
					],
					columns: [
						{
							label: t('Type'),
							fieldname: 'deploy_type',
							width: 0.3,
						},
						{
							label: t('Status'),
							fieldname: 'status',
							type: 'Badge',
							width: 0.5,
						},
						// {
						// 	label: t('Backup'),
						// 	width: 0.4,
						// 	type: 'Component',
						// 	component({ row }) {
						// 		return h(
						// 			'div',
						// 			{
						// 				class: 'truncate text-base',
						// 			},
						// 			row.skipped_backups
						// 				? 'Skipped'
						// 				: row.backup_type || 'Logical',
						// 		);
						// 	},
						// },
						{
							label: t('Created By'),
							fieldname: 'owner',
						},
						{
							label: t('Scheduled At'),
							fieldname: 'scheduled_time',
							format(value) {
								return date(value, 'lll')
							},
						},
						{
							label: t('Updated On'),
							fieldname: 'updated_on',
							format(value) {
								return date(value, 'lll')
							},
						},
					],
					rowActions({ row, documentResource: site }) {
						return [
							{
								label: t('Edit'),
								condition: () => row.status === 'Scheduled',
								onClick() {
									let SiteUpdateDialog = defineAsyncComponent(
										() => import('../components/SiteUpdateDialog.vue'),
									)
									renderDialog(
										h(SiteUpdateDialog, {
											site: site.doc?.name,
											existingUpdate: row.name,
										}),
									)
								},
							},
							{
								label: t('Cancel'),
								condition: () => row.status === 'Scheduled',
								onClick() {
									confirmDialog({
										title: t('Cancel Update'),
										message: t('Are you sure you want to cancel the scheduled update?'),
										onSuccess({ hide }) {
											if (site.cancelUpdate.loading) return
											toast.promise(
												site.cancelUpdate.submit({ site_update: row.name }),
												{
													loading: t('Cancelling update...'),
													success: () => {
														hide()
														site.reload()
														return t('Update cancelled')
													},
													error: (e) => getToastErrorMessage(e),
												},
											)
										},
									})
								},
							},
							{
								label: t('View Job'),
								condition: () =>
									!['Scheduled', 'Cancelled'].includes(row.status),
								onClick() {
									router.push({
										name: 'Site Update',
										params: { id: row.name },
									})
								},
							},
							{
								label: t('Update Now'),
								condition: () => row.status === 'Scheduled',
								onClick() {
									let siteUpdate = getDocResource({
										doctype: 'Site Update',
										name: row.name,
										whitelistedMethods: {
											updateNow: 'start',
										},
									})

									toast.promise(siteUpdate.updateNow.submit(), {
										loading: t('Updating site...'),
										success: () => {
											router.push({
												name: 'Site Update',
												params: { id: row.name },
											})

											return t('Site update started')
										},
										error: 'Failed to update site',
									})
								},
							},
							{
								label: t('View App Changes'),
								onClick() {
									createListResource({
										doctype: 'Deploy Candidate Difference App',
										fields: [
											'difference.github_diff_url as diff_url',
											'difference.source_hash as source_hash',
											'difference.destination_hash as destination_hash',
											'app.title as app',
										],
										filters: {
											parenttype: 'Deploy Candidate Difference',
											parent: row.difference,
										},
										auto: true,
										pageLength: 99,
										onSuccess(data) {
											if (data?.length) {
												renderDialog(
													h(
														GenericDialog,
														{
															options: {
																title: t('App Changes'),
																size: '2xl',
															},
														},
														{
															default: () =>
																h(ObjectList, {
																	options: {
																		data: () => data,
																		columns: [
																			{
																				label: t('App'),
																				fieldname: 'app',
																			},
																			{
																				label: t('From'),
																				fieldname: 'source_hash',
																				type: 'Button',
																				Button({ row }) {
																					return {
																						label:
																							row.source_tag ||
																							row.source_hash.slice(0, 7),
																						variant: 'ghost',
																						class: 'font-mono',
																						link: `${
																							row.diff_url.split('/compare')[0]
																						}/commit/${row.source_hash}`,
																					}
																				},
																			},
																			{
																				label: t('To'),
																				fieldname: 'destination_hash',
																				type: 'Button',
																				Button({ row }) {
																					return {
																						label:
																							row.destination_tag ||
																							row.destination_hash.slice(0, 7),
																						variant: 'ghost',
																						class: 'font-mono',
																						link: `${
																							row.diff_url.split('/compare')[0]
																						}/commit/${row.destination_hash}`,
																					}
																				},
																			},
																			{
																				label: t('App Changes'),
																				fieldname: 'diff_url',
																				align: 'right',
																				type: 'Button',
																				Button({ row }) {
																					return {
																						label: t('View'),
																						variant: 'ghost',
																						slots: {
																							prefix: icon('external-link'),
																						},
																						link: row.diff_url,
																					}
																				},
																			},
																		],
																	},
																}),
														},
													),
												)
											} else
												toast.error(
													t(
														'No app changes found. The current and target benches run the same app versions, so there is nothing to update.',
													),
												)
										},
									})
								},
							},
						]
					},
					actions({ documentResource: site }) {
						if (site.doc.group_public) return []

						return [
							{
								label: t('Configure'),
								slots: {
									prefix: icon('settings'),
								},
								onClick() {
									let ConfigureAutoUpdateDialog = defineAsyncComponent(
										() =>
											import(
												'../components/site/ConfigureAutoUpdateDialog.vue'
											),
									)

									renderDialog(
										h(ConfigureAutoUpdateDialog, {
											site: site.doc?.name,
										}),
									)
								},
							},
						]
					},
					extraResource({ listResource: updates }) {
						const latest = updates?.data?.[0]
						if (latest?.status !== 'Cancelled') return
						return {
							type: 'list',
							doctype: 'Press Notification',
							fields: ['message'],
							filters: {
								document_type: 'Site Update',
								document_name: latest.name,
								// the tab itself opens for support, so the banner must too
								skip_team_filter_for_system_user_and_support_agent: true,
							},
							limit: 1,
							auto: true,
						}
					},
					banner({ documentResource: site, extraResource: notification }) {
						const message = notification?.data?.[0]?.message
						if (message) {
							return { title: message, type: 'warning' }
						}
						const bannerTitle =
							'Your site is currently on a shared bench. Upgrade to a private bench to configure auto updates and <a href="https://frappecloud.com/shared-hosting#benches" class="underline" target="_blank">more</a>.'
						return getUpsellBanner(site, bannerTitle)
					},
				},
			},
			{
				label: t('Actions'),
				icon: icon('sliders'),
				route: 'actions',
				type: 'Component',
				condition: (site) => {
					return site.doc?.status !== 'Archived'
				},
				component: SiteActions,
				props: (site) => {
					return { site: site.doc?.name }
				},
			},

			{
				label: t('Activity'),
				icon: icon('activity'),
				route: 'activity',
				type: 'list',
				list: {
					doctype: 'Site Activity',
					filters: (site) => {
						return { site: site.doc?.name }
					},
					fields: ['owner', 'job'],
					orderBy: 'creation desc',
					route(row) {
						if (!row.job) return {}

						return {
							name: 'Site Job',
							params: { id: row.job },
						}
					},
					columns: [
						{
							label: t('Action'),
							fieldname: 'action',
							format(value, row) {
								let action = row.action
								if (action == 'Create') {
									action = 'Site created'
								}
								return `${action} by ${getActorName(row.owner)}`
							},
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
									'Activate Site',
									'Add Domain',
									'Archive',
									'Backup',
									'Create',
									'Clear Cache',
									'Deactivate Site',
									'Disable Database Access',
									'Drop Offsite Backups',
									'Enable Database Access',
									'Install App',
									'Login as Administrator',
									'Migrate',
									'Reinstall',
									'Restore',
									'Suspend Site',
									'Uninstall App',
									'Unsuspend Site',
									'Update',
									'Update Configuration',
								],
							},
						]
					},
				},
			},

			{
				label: t('Plan History'),
				icon: icon('credit-card'),
				route: 'plan-history',
				type: 'list',
				list: {
					doctype: 'Site Plan Change',
					filters: (site) => {
						return { site: site.doc?.name }
					},
					fields: ['from_plan', 'to_plan', 'type', 'timestamp', 'owner'],
					orderBy: 'timestamp desc',
					columns: [
						{
							label: t('Changed From'),
							fieldname: 'from_plan',
							class: 'text-ink-gray-6',
							format(value) {
								return value || '—'
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
								if (value === 'Upgrade') return 'green'
								if (value === 'Downgrade') return 'red'
								return 'gray'
							},
						},
						{
							label: t('Changed By'),
							fieldname: 'owner',
							class: 'text-ink-gray-6',
						},
						{
							label: t('Date'),
							fieldname: 'timestamp',
							type: 'Timestamp',
							align: 'right',
						},
					],
				},
			},
		],
		actions(context) {
			let { documentResource: site } = context
			let $team = getTeam()
			let runningJobs = getRunningJobs({ site: site.doc?.name })

			return [
				{
					label: t('Jobs in progress'),
					slots: {
						prefix: () => h(LoadingIndicator, { class: 'w-4 h-4' }),
					},
					condition() {
						return (
							runningJobs.filter((job) =>
								['Pending', 'Running'].includes(job.status),
							).length > 0
						)
					},
					onClick() {
						router.push({
							name: 'Site Jobs',
							params: { name: site.name },
						})
					},
				},
				{
					label: t('Update Available'),
					variant: site.doc?.setup_wizard_complete ? 'solid' : 'subtle',
					slots: {
						prefix: icon('alert-circle'),
					},
					condition() {
						return (
							!canRestoreTables(site) &&
							!site.doc?.has_scheduled_updates &&
							site.doc.update_information?.update_available &&
							['Active', 'Inactive', 'Suspended', 'Broken'].includes(
								site.doc.status,
							)
						)
					},

					onClick() {
						let SiteUpdateDialog = defineAsyncComponent(
							() => import('../components/SiteUpdateDialog.vue'),
						)
						renderDialog(h(SiteUpdateDialog, { site: site.doc?.name }))
					},
				},
				{
					label: t('Update Scheduled'),
					slots: {
						prefix: icon('calendar'),
					},
					condition: () => site.doc?.has_scheduled_updates,
					onClick() {
						router.push({
							name: 'Site Detail Updates',
							params: { name: site.name },
						})
					},
				},
				{
					label: t('Restore Tables'),
					variant: 'solid',
					slots: {
						prefix: icon('database'),
					},
					condition: () => canRestoreTables(site),
					onClick: () => confirmRestoreTables(site),
				},
				{
					label: t('Enable Monitoring'),
					slots: {
						prefix: icon('activity'),
					},
					condition: () => site.doc?.is_monitoring_disabled,
					onClick() {
						let SiteEnableMonitoringDialog = defineAsyncComponent(
							() => import('../components/site/SiteEnableMonitoringDialog.vue'),
						)
						renderDialog(
							h(SiteEnableMonitoringDialog, { site: site.doc?.name }),
						)
					},
				},
				{
					label: t('Impersonate Site Owner'),
					title: t('Impersonate Site Owner'), // for label to pop-up on hover
					slots: {
						icon: defineAsyncComponent(async () => {
							const mod = await import('~icons/lucide/venetian-mask')
							return {
								render() {
									return h(mod.default, { class: 'w-5 h-5' })
								},
							}
						}),
					},
					condition: () =>
						$team.doc?.is_desk_user && site.doc.team !== $team.name,
					onClick() {
						switchToTeam(site.doc.team)
					},
				},
				{
					label: t('Visit Site'),
					slots: {
						prefix: icon('external-link'),
					},
					condition: () =>
						site.doc.status !== 'Archived' && site.doc?.setup_wizard_complete,
					onClick() {
						let siteURL = `https://${site.name}`
						if (
							site.doc.version === 'Nightly' ||
							Number(site.doc.version.split(' ')[1]) >= 15
						)
							siteURL += '/apps'
						window.open(siteURL, '_blank')
					},
				},
				{
					label: t('Setup Site'),
					slots: {
						prefix: icon('external-link'),
					},
					variant: 'solid',
					loading: site.loginAsAdmin.loading || site.loginAsTeam.loading,
					condition: () =>
						site.doc.status === 'Active' && !site.doc?.setup_wizard_complete,
					onClick() {
						if (site.doc.additional_system_user_created) {
							site.loginAsTeam
								.submit({ reason: '' })
								.then((url) => window.open(url, '_blank'))
						} else {
							site.loginAsAdmin
								.submit({ reason: '' })
								.then((url) => window.open(url, '_blank'))
						}
					},
				},
				{
					label: t('Options'),
					context,
					options: [
						{
							label: t('View in Desk'),
							icon: 'external-link',
							condition: () => $team.doc?.is_desk_user,
							onClick: () => {
								window.open(
									`${window.location.protocol}//${window.location.host}/app/site/${site.name}`,
									'_blank',
								)
							},
						},
						{
							label: t('Login As Administrator'),
							icon: 'external-link',
							condition: () => ['Active', 'Broken'].includes(site.doc.status),
							onClick: () => {
								confirmDialog({
									title: t('Login as Administrator'),
									message: tr(
										'Are you sure you want to login as administrator on the site <b>{name}</b>?',
										{ name: site.doc?.name },
									),
									fields:
										$team.name !== site.doc.team || $team.doc.is_desk_user
											? [
													{
														label: t('Reason'),
														type: 'textarea',
														fieldname: 'reason',
														default: LOGIN_REASON_PREFIX,
													},
												]
											: [],
									onSuccess: ({ hide, values }) => {
										const reason = values.reason?.trim()
										if (
											(!reason || reason === LOGIN_REASON_PREFIX.trim()) &&
											($team.name !== site.doc.team || $team.doc.is_desk_user)
										) {
											throw new Error(
												'Reason is required. Enter why you are logging in as Administrator before continuing.',
											)
										}
										return site.loginAsAdmin
											.submit({ reason: values.reason })
											.then((result) => {
												let url = result
												window.open(url, '_blank')
												hide()
											})
									},
								})
							},
						},
					],
				},
			]
		},
	},

	routes: [
		{
			name: 'Site Backup Audit Trail',
			path: 'backups/audit-trail',
			component: () => import('../components/site/SiteBackupAuditTrail.vue'),
		},
		{
			name: 'Site Update',
			path: 'updates/:id',
			component: () => import('../pages/SiteUpdate.vue'),
		},
		{
			name: 'Site Migration',
			path: 'migrations/:id',
			component: () => import('../pages/SiteMigration.vue'),
		},
	],
}
