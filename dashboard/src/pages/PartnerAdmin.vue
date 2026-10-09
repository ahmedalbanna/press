<script setup lang="ts">
import { getTeam } from '@/data/team';
import { t } from '../utils/language'

const $team = getTeam();
defineOptions({ name: 'PartnerAdmin' });

const tabs = [
	{ label: t('Partner List'), route: { name: 'PartnerList' } },
	{ label: t('Certificates'), route: { name: 'CertificateList' } },
	{ label: t('Leads'), route: { name: 'PartnerAdminLeads' } },
	{ label: t('Resources'), route: { name: 'PartnerAdminResources' } },
	{ label: t('Audits'), route: { name: 'PartnerAdminAudits' } },
];
</script>

<template>
	<div v-if="$team?.doc?.is_desk_user" class="flex h-screen">
		<aside class="flex flex-col p-2 border-r">
			<router-link
				v-for="tab in tabs"
				:key="tab.label"
				:to="tab.route"
				class="text-base text-ink-gray-5 py-2 px-3.5 pr-15 transition-colors hover:bg-surface-gray-2 rounded"
				active-class="bg-surface-gray-2 text-ink-gray-9"
			>
				{{ tab.label }}
			</router-link>
		</aside>

		<router-view class="flex-1 overflow-auto" />
	</div>

	<div
		v-else
		class="mx-auto mt-60 w-fit rounded border border-b px-12 py-8 text-center text-ink-gray-6"
	>
		<lucide-alert-triangle class="mx-auto mb-4 h-6 w-6 text-red-600" />
		<ErrorMessage message="You aren't permitted to view the billing page" />
	</div>
</template>
