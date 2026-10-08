<template>
	<div class="flex items-center justify-between gap-1">
		<div>
			<h3 class="text-base font-medium">{{ t(props.actionLabel) }}</h3>
			<p class="mt-1 text-p-base text-ink-gray-6">{{ t(props.description) }}</p>
		</div>
		<Button
			v-if="site?.doc"
			class="whitespace-nowrap"
			@click="getSiteActionHandler(props.actionLabel)"
		>
			<p
				:class="
					group === 'Dangerous Actions' ? 'text-red-600' : 'text-ink-gray-8'
				"
			>
				{{ t(props.buttonLabel) }}
			</p>
		</Button>
	</div>
</template>

<script setup>
import { debounce, getCachedDocumentResource } from 'frappe-ui';
import { defineAsyncComponent, h, onMounted } from 'vue';
import { toast } from 'vue-sonner';
import { confirmDialog, renderDialog } from '../utils/components';
import { getToastErrorMessage } from '../utils/toast';
import router from '../router';
import { isLastSite } from '../data/team';
import CommunicationInfoDialog from './CommunicationInfoDialog.vue';
import { useRoute } from 'vue-router';
import { t, tr } from '../utils/language';

const props = defineProps({
	siteName: { type: String, required: true },
	actionLabel: { type: String, required: true },
	method: { type: String, required: true },
	description: { type: String, required: true },
	buttonLabel: { type: String, required: true },
	group: { type: String, required: false },
});

const site = getCachedDocumentResource('Site', props.siteName);
const route = useRoute();

onMounted(() => {
	const queryAction = route.query['action'];
	if (props.actionLabel === queryAction) {
		getSiteActionHandler(queryAction);
	}
});

function getSiteActionHandler(action) {
	const actionDialogs = {
		'Manage Product Warranty': defineAsyncComponent(
			() => import('./ManageProductWarrantyDialog.vue'),
		),
		'Configure compute allocation': defineAsyncComponent(
			() => import('./ConfigureComputeAllocationDialog.vue'),
		),
		'Restore with files': defineAsyncComponent(
			() => import('./SiteDatabaseRestoreDialog.vue'),
		),
		'Restore from an existing site': defineAsyncComponent(
			() => import('./site/SiteDatabaseRestoreFromURLDialog.vue'),
		),
		'Manage database users': defineAsyncComponent(
			() => import('./SiteDatabaseAccessDialog.vue'),
		),
		'Version upgrade': defineAsyncComponent(
			() => import('./site/SiteVersionUpgradeDialog.vue'),
		),
		'Schedule backup': defineAsyncComponent(
			() => import('./site/SiteScheduleBackup.vue'),
		),
	};
	if (actionDialogs[action]) {
		const dialog = h(actionDialogs[action], { site: site.doc.name });
		renderDialog(dialog);
		return;
	}

	const actionHandlers = {
		'Notification Settings': onNotificationSettings,
		'Activate site': onActivateSite,
		'Deactivate site': onDeactivateSite,
		'Drop site': onDropSite,
		'Migrate site': onMigrateSite,
		'Transfer site': onTransferSite,
		'Reset site': onSiteReset,
		'Clear cache': onClearCache,
		'Schedule backup': onScheduleBackup,
	};
	if (actionHandlers[action]) {
		actionHandlers[action].call(this);
	}
}

function onNotificationSettings() {
	return renderDialog(
		h(CommunicationInfoDialog, {
			referenceDoctype: 'Site',
			referenceName: site.doc.name,
		}),
	);
}

function onDeactivateSite() {
	return confirmDialog({
		title: t('Deactivate Site'),
		message: t(
			'Are you sure you want to deactivate this site?<br><br><div class="text-bg-base bg-surface-gray-2 p-2 rounded-md">The site will go in an <strong>inactive</strong> state. It won\'t be accessible and background jobs won\'t run. <br><br><div class="text-red-600">You will still be charged for it.</div></div>',
		),
		primaryAction: {
			label: t('Deactivate'),
			variant: 'solid',
			theme: 'red',
			onClick({ hide }) {
				return site.deactivate.submit().then(hide);
			},
		},
	});
}

function onActivateSite() {
	return confirmDialog({
		title: t('Activate Site'),
		message: t(
			'Are you sure you want to activate this site?<br><br><strong>Note: Use this as last resort if site is broken and inaccessible</strong>',
		),
		primaryAction: {
			label: t('Activate'),
			variant: 'solid',
			onClick({ hide }) {
				return site.activate.submit().then(hide);
			},
		},
	});
}

function onDropSite() {
	const ArchiveSiteDialog = defineAsyncComponent(
		() => import('./site/ArchiveSiteDialog.vue'),
	);

	return renderDialog(
		h(ArchiveSiteDialog, {
			site: site,
			modelValue: true,
		}),
	);
}

function onMigrateSite() {
	return confirmDialog({
		title: t('Migrate Site'),
		message: t(
			'<span class="rounded-sm bg-surface-gray-2 p-0.5 font-mono text-sm font-semibold">bench migrate</span> command will be executed on your site. Are you sure you want to run this command? We recommend that you take a database backup before continuing.',
		),
		fields: [
			{
				label: t('Skip patches if they fail during migration (Not recommended)'),
				fieldname: 'skipFailingPatches',
				type: 'checkbox',
			},
			{
				label: t('Please type the site name to confirm.'),
				fieldname: 'confirmSiteName',
			},
		],
		primaryAction: {
			label: t('Migrate'),
			variant: 'solid',
			theme: 'red',
			onClick: ({ hide, values }) => {
				if (values.confirmSiteName !== site.doc.name) {
					throw new Error(t('Site name does not match'));
				}
				return site.migrate
					.submit({ skip_failing_patches: values.skipFailingPatches })
					.then(hide);
			},
		},
	});
}

function onSiteReset() {
	return confirmDialog({
		title: t('Reset Site'),
		message: t(
			'All the data from your site will be lost. Are you sure you want to reset your database?',
		),
		fields: [
			{
				label: t('Please type the site name to confirm.'),
				fieldname: 'confirmSiteName',
			},
		],
		primaryAction: {
			label: t('Reset'),
			variant: 'solid',
			theme: 'red',
			onClick: ({ hide, values }) => {
				if (values.confirmSiteName !== site.doc.name) {
					throw new Error(t('Site name does not match.'));
				}
				return site.reinstall.submit().then(hide);
			},
		},
	});
}

function onTransferSite() {
	return confirmDialog({
		title: t('Transfer Site Ownership'),
		fields: [
			{
				label: t('Enter email address of the team for transfer of site ownership'),
				fieldname: 'email',
			},
			{
				label: t('Reason for transfer'),
				fieldname: 'reason',
				type: 'textarea',
			},
		],
		primaryAction: {
			label: t('Transfer'),
			variant: 'solid',
			onClick: ({ hide, values }) => {
				return site.sendTransferRequest
					.submit({ team_mail_id: values.email, reason: values.reason || '' })
					.then(() => {
						hide();
						toast.success(
							tr('Transfer request sent to {email} successfully.', {
								email: values.email,
							}),
						);
					});
			},
		},
	});
}

function onClearCache() {
	return confirmDialog({
		title: t('Clear Cache'),
		message: t(
			'<span class="rounded-sm bg-surface-gray-2 p-0.5 font-mono text-sm font-semibold">bench clear-cache</span> and <span class="rounded-sm bg-surface-gray-2 p-0.5 font-mono text-sm font-semibold">bench clear-website-cache</span> commands will be executed on your site. Are you sure you want to run these commands?',
		),
		primaryAction: {
			label: t('Clear Cache'),
			variant: 'solid',
			onClick: ({ hide }) => {
				return site.clearSiteCache.submit().then(hide);
			},
		},
	});
}

function onScheduleBackup() {
	router.push({
		name: 'Site Detail Backups',
		params: { name: site.doc.name },
	});
}
</script>
