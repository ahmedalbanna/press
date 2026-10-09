<template>
	<div class="flex h-full flex-col">
		<div class="sticky top-0 z-10 shrink-0">
			<Header>
				<FBreadcrumbs
					:items="[
						{ label: t('Partnership'), route: { name: 'PartnerLeads' } },
						{ label: t('Partner Lead'), route: { name: 'PartnerLeads' } },
						{ label: lead.doc?.organization_name, route: '#' },
					]"
				/>
				<div>
					<Button
						v-if="$session.isSystemUser"
						:variant="'subtle'"
						:label="t('View in Desk')"
						@click="openIndDesk()"
					/>
				</div>
			</Header>
		</div>
		<TabsWithRouter :tabs="tabs" />
	</div>
</template>
<script>
import Header from '../components/Header.vue';
import { Breadcrumbs, Tabs } from 'frappe-ui';
import TabsWithRouter from '../components/TabsWithRouter.vue';
import { t } from '../utils/language'
export default {
	name: 'PartnerLeadDetails',
	components: {
		Header,
		FBreadcrumbs: Breadcrumbs,
		FTabs: Tabs,
		TabsWithRouter,
	},
	resources: {
		lead() {
			return {
				type: 'document',
				doctype: 'Partner Lead',
				name: this.$route.params.leadId,
			};
		},
	},
	data() {
		return {
			currentTab: 0,
			tabs: [
				{ label: t('Overview'), route: { name: 'LeadOverview' } },
				{ label: t('Follow-up'), route: { name: 'LeadDealDetails' } },
				{ label: t('Activities'), route: { name: 'LeadActivities' } },
			],
		};
	},
	computed: {
		lead() {
			return this.$resources.lead;
		},
	},
	methods: {
		openIndDesk() {
			const deskUrl = `${window.location.protocol}//${window.location.host}/app/partner-lead/${this.lead.name}`;
			window.open(deskUrl, '_blank');
		},
	},
};
</script>
